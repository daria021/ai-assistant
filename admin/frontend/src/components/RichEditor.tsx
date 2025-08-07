import {forwardRef, useEffect, useImperativeHandle, useRef, useState,} from 'react';
import type {Emoji, MessageEntityDTO} from '../services/api';

/* ───────── константы ───────── */
const RHINO = '🦏';          // плейсхолдер
const RHINO_LEN = 2;         // 1 юникод-символ = 2 UTF-16 code units
// очередь ID для восстановления эмодзи
const idsRef = {current: [] as string[]};

/* ───────── наружу отдаём только insertEmoji ───────── */
export type RichEditorHandle = {
    insertEmoji: (emoji: Emoji) => void;
};

export interface RichEditorProps {
    emojis: Emoji[];
    initialContent?: string;
    onChange: (payload: {
        html: string;
        text: string;
        entities: MessageEntityDTO[];
    }) => void;
}

export const RichEditor = forwardRef<RichEditorHandle, RichEditorProps>(
    ({emojis, initialContent = '', onChange}, ref) => {

        const editorRef = useRef<HTMLDivElement>(null);
        const [isUrlModalOpen, setIsUrlModalOpen] = useState(false);
        const [pendingUrl, setPendingUrl] = useState('');
        const savedRangeRef = useRef<Range | null>(null);

        const openUrlModal = () => {
            const sel = window.getSelection();
            if (sel && sel.rangeCount > 0) {
                savedRangeRef.current = sel.getRangeAt(0).cloneRange();
            }
            setPendingUrl('');
            setIsUrlModalOpen(true);
        };
        const closeUrlModal = () => setIsUrlModalOpen(false);
        const handleInsertUrl = () => {
            if (pendingUrl.trim() && savedRangeRef.current) {
                const sel = window.getSelection();
                sel?.removeAllRanges();
                sel?.addRange(savedRangeRef.current);
                wrapSelection('a', {href: pendingUrl.trim(), target: '_blank'});
            }
            closeUrlModal();
        };

        // очередь ID для восстановления эмодзи
        function wrapSelection(tagName: string, attrs: Record<string, string> = {}) {
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0) return;
            const range = sel.getRangeAt(0);
            if (range.collapsed) return;

            const editor = editorRef.current;
            if (!editor) return;
            console.log("editor", editor);
            editor.focus();

            const wrapper = document.createElement(tagName);
            for (const [k, v] of Object.entries(attrs)) {
                wrapper.setAttribute(k, v);
            }

            wrapper.appendChild(range.extractContents());

            range.insertNode(wrapper);

            const newSel = window.getSelection();
            if (newSel && editor) {
                newSel.removeAllRanges();
                const r = document.createRange();
                r.selectNodeContents(editor);
                r.collapse(false); // в конец
                newSel.addRange(r);
            }

            editor.dispatchEvent(new Event('input'));
        }

        // возвращает URL эмодзи по его custom_emoji_id
        const getUrlById = (id: string): string => {
            const found = emojis.find(e => e.custom_emoji_id === id);
            return found ? found.img_url : '';
        };


        /* ставим начальный HTML один раз */
        useEffect(() => {
            if (editorRef.current) editorRef.current.innerHTML = initialContent;
            // сразу пробрасываем initialContent наружу
            if (editorRef.current) handleInput();
            // eslint-disable-next-line react-hooks/exhaustive-deps
        }, []);

        /* ---------- универсальная сериализация ---------- */
        const serialize = (el: HTMLDivElement) => {
            const clone = el.cloneNode(true) as HTMLDivElement;
            const ids: string[] = [];

            // 1) заменяем все <img> и <video> emoji на плейсхолдер RHINO и собираем их ID
            clone
                .querySelectorAll('img[data-custom-emoji-id],video[data-custom-emoji-id]')
                .forEach(node => {
                    const id = node.getAttribute('data-custom-emoji-id')!
                    ids.push(id)
                    node.parentNode!.replaceChild(
                        document.createTextNode(RHINO),
                        node
                    )
                })
            idsRef.current = ids

            // 2) получаем html и plain-text
            const html = el.innerHTML
            const text = clone.innerText.replace(/\n/g, '\r\n')

            // 3) рассчитываем сущности
            const entities: MessageEntityDTO[] = []
            const walker = document.createTreeWalker(clone, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, null)
            let offset = 0
            console.log("BEGIN")

            while (walker.nextNode()) {
                const node = walker.currentNode

                // текстовые куски
                console.log("node.nodeType === Node.TEXT_NODE")
                console.log(node.nodeType === Node.TEXT_NODE)
                if (node.nodeType === Node.TEXT_NODE) {
                    const text = (node as Text).data.replace(/\n/g, '\r\n')
                    console.log("text.length")
                    console.log(text.length)
                    offset += text.length
                    continue
                }

                // элементы форматирования
                const eln = node as HTMLElement
                const inner = eln.innerText.replace(/\n/g, '\r\n')
                let type: MessageEntityDTO['type'] | null = null

                switch (eln.tagName) {
                    case 'B':
                        type = 'bold';
                        break
                    case 'I':
                        type = 'italic';
                        break
                    case 'U':
                        type = 'underline';
                        break
                    case 'S':
                        type = 'strikethrough';
                        break
                    case 'A':
                        type = 'text_link';
                        break
                }

                if (!type) continue

                // сформировать сущность
                let entity: MessageEntityDTO = {type, offset, length: inner.length};
                if (type === 'text_link') {
                    entity = {
                        type: 'text_link',
                        offset,
                        length: inner.length,
                        url: eln.getAttribute('href') || undefined
                    };
                }
                entities.push(entity);

                // сдвинуть offset на длину этого фрагмента
                console.log("inner.length")
                console.log(inner.length)
                offset += inner.length
            }

            // 4) добавляем кастом-эмодзи
            const rx = new RegExp(RHINO, 'g')
            let match: RegExpExecArray | null
            let i = 0

            while ((match = rx.exec(text))) {
                entities.push({
                    type: 'custom_emoji',
                    offset: match.index,
                    length: RHINO_LEN,
                    custom_emoji_id: ids[i++] || '',
                } as MessageEntityDTO)
            }

            return {html, text, entities}
        }


        function restoreRhinos(root: HTMLElement) {
            const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
            const textNodes: Text[] = [];

            while (walker.nextNode()) {
                const node = walker.currentNode as Text;
                if (node.nodeValue?.includes('🦏')) textNodes.push(node);
            }

            textNodes.forEach(textNode => {
                const parts = textNode.nodeValue!.split('🦏');
                const frag = document.createDocumentFragment();

                parts.forEach((part, idx) => {
                    frag.appendChild(document.createTextNode(part));
                    if (idx < parts.length - 1) {
                        const emojiId = idsRef.current.shift()!;
                        const img = document.createElement('img');
                        img.setAttribute('data-custom-emoji-id', emojiId);
                        img.src = getUrlById(emojiId);  // ваша функция получения URL по id
                        img.width = img.height = 24;
                        frag.appendChild(img);
                    }
                });

                textNode.parentNode!.replaceChild(frag, textNode);
            });
        }


        /* ---------- единый обработчик input ---------- */
        const handleInput = () => {
            const el = editorRef.current;
            if (!el) return;

            // сначала сериализуем и сохраняем ids
            const result = serialize(el);

            console.group('%cRichEditor Input Result', 'color: teal; font-weight: bold;');
            console.log('HTML:', result.html);
            console.log('Text:', result.text);
            console.log('Entities:', result.entities);
            console.groupEnd();
            // тут же восстанавливаем все 🦏 → <img>
            restoreRhinos(el);

            // отдаём готовые html/text/entities
            onChange(result);
        };


        useEffect(() => {
            const el = editorRef.current;
            if (!el) return;
            el.addEventListener('input', handleInput);
            return () => el.removeEventListener('input', handleInput);
        }, []);

        /* ---------- логика вставки эмодзи ---------- */
        const insertEmoji = (emoji: Emoji) => {
            const el = editorRef.current;
            if (!el) return;

            let sel = window.getSelection();
            const inEditor =
                sel && sel.rangeCount > 0 && el.contains(sel.getRangeAt(0).startContainer);

            if (!inEditor) {
                el.focus();
                const r = document.createRange();
                r.selectNodeContents(el);
                r.collapse(false);
                sel?.removeAllRanges();
                sel?.addRange(r);
            }

            sel = window.getSelection();
            if (!sel || !sel.rangeCount) return;

            const range = sel.getRangeAt(0);
            range.deleteContents();

            const isVideo =
                emoji.format === 'video' ||
                emoji.img_url.toLowerCase().endsWith('.webm');

            const node: HTMLElement = isVideo
                ? (() => {
                    const v = document.createElement('video');
                    v.src = emoji.img_url;
                    v.loop = true;
                    v.muted = true;
                    v.autoplay = true;
                    v.playsInline = true;
                    v.width = v.height = 24;
                    return v;
                })()
                : (() => {
                    const i = document.createElement('img');
                    i.src = emoji.img_url;
                    i.alt = emoji.name;
                    i.width = i.height = 24;
                    return i;
                })();

            node.setAttribute('data-custom-emoji-id', emoji.custom_emoji_id);
            node.style.display = 'inline-block';
            node.style.verticalAlign = 'middle';

            range.insertNode(node);
            range.setStartAfter(node);
            sel.removeAllRanges();
            sel.addRange(range);

            /* триггерим input, чтобы сериализовать новый контент */
            el.dispatchEvent(new Event('input'));
        };

        /* отдаём наружу только insertEmoji */
        useImperativeHandle(ref, () => ({insertEmoji}), [insertEmoji]);

        return (
            <div className="relative">
                {/* ——— Панель кнопок форматирования ——— */}
                <div className="flex items-center mb-2 space-x-1">
                    <button
                        type="button"
                        onClick={() => wrapSelection('b')}
                        className="px-2 py-1 border rounded"
                    ><b>Ж</b></button>

                    <button
                        type="button"
                        onClick={() => wrapSelection('i')}
                        className="px-2 py-1 border rounded"
                    ><i>К</i></button>

                    <button
                        type="button"
                        onClick={() => wrapSelection('u')}
                        className="px-2 py-1 border rounded"
                    ><u>П</u></button>

                    <button
                        type="button"
                        onClick={() => wrapSelection('s')}
                        className="px-2 py-1 border rounded"
                    ><s>З</s></button>

                    <button
                        type="button"
                        onClick={openUrlModal}
                        className="px-2 py-1 border rounded"
                    >🔗
                    </button>
                </div>

                <div
                    ref={editorRef}
                    contentEditable
                    suppressContentEditableWarning
                    className="border p-2 rounded min-h-[150px] focus:outline-none"
                />

                {isUrlModalOpen && (
                    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
                        <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md relative">
                            <button
                                onClick={closeUrlModal}
                                className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
                            >
                                ✕
                            </button>
                            <h2 className="text-xl font-semibold mb-4">Вставить ссылку</h2>
                            <input
                                type="url"
                                placeholder="https://example.com"
                                value={pendingUrl}
                                onChange={e => setPendingUrl(e.target.value)}
                                className="w-full mb-4 p-2 border rounded focus:ring-2 focus:ring-brand"
                                autoFocus
                            />
                            <button
                                onClick={handleInsertUrl}
                                className="w-full py-2 bg-brand text-white rounded hover:bg-brand transition"
                            >
                                Вставить
                            </button>
                        </div>
                    </div>
                )}
            </div>
        );
    },
);
RichEditor.displayName = 'RichEditor';
