import {forwardRef, useEffect, useImperativeHandle, useRef, useState} from 'react';
import type {Emoji, MessageEntityDTO} from '../services/api';

/* ───────── константы ───────── */
const RHINO = '🦏';
const RHINO_LEN = 2;
const idsRef = {current: [] as string[]};

/* ───────── наружу отдаём только insertEmoji ───────── */
export type RichEditorHandle = { insertEmoji: (emoji: Emoji) => void };

export interface RichEditorProps {
    emojis: Emoji[];
    initialContent?: string;
    onChange: (payload: { html: string; text: string; entities: MessageEntityDTO[] }) => void;
}

export const RichEditor = forwardRef<RichEditorHandle, RichEditorProps>(
    ({emojis, initialContent = '', onChange}, ref) => {

        const editorRef = useRef<HTMLDivElement>(null);
        const [isUrlModalOpen, setIsUrlModalOpen] = useState(false);
        const [pendingUrl, setPendingUrl] = useState('');
        const savedRangeRef = useRef<Range | null>(null);

        /* ───────── plain-text вставка ───────── */
        const htmlToPlain = (html: string): string => {
            const tmp = document.createElement('div');
            tmp.innerHTML = html;
            return tmp.innerText.replace(/\u00A0/g, ' ');
        };

        const insertPlainTextAtSelection = (text: string) => {
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0) return;

            const range = sel.getRangeAt(0);
            range.deleteContents();

            // пробуем нативный вставщик чистого текста
            if (document.queryCommandSupported?.('insertText')) {
                document.execCommand('insertText', false, text);
            } else {
                // fallback: руками — текстовые ноды + <br> на переводах строк
                const lines = text.split(/\r\n|\n|\r/);
                const frag = document.createDocumentFragment();
                lines.forEach((line, i) => {
                    frag.appendChild(document.createTextNode(line));
                    if (i < lines.length - 1) frag.appendChild(document.createElement('br'));
                });
                range.insertNode(frag);
                // курсор в конец
                sel.removeAllRanges();
                const r2 = document.createRange();
                r2.selectNodeContents(editorRef.current as HTMLDivElement);
                r2.collapse(false);
                sel.addRange(r2);
            }

            editorRef.current?.dispatchEvent(new Event('input'));
        };

        // Жёсткая фильтрация вставки/дропа: только plain text
        useEffect(() => {
            const el = editorRef.current;
            if (!el) return;

            const handlePlainInsert = (text?: string, html?: string) => {
                const t = text && text.length ? text : (html ? htmlToPlain(html) : '');
                if (t) insertPlainTextAtSelection(t);
            };

            // самый ранний хук
            const onBeforeInput = (e: InputEvent) => {
                const t: string = e?.inputType;
                if (t === 'insertFromPaste' || t === 'insertFromPasteAsQuotation' || t === 'insertFromDrop') {
                    e.preventDefault();
                    const dt: DataTransfer | null = e.dataTransfer ?? null;
                    const text = dt?.getData('text/plain') ?? '';
                    const html = dt?.getData('text/html') ?? '';
                    handlePlainInsert(text, html);
                }
            };

            const onPaste = (e: ClipboardEvent) => {
                e.preventDefault();
                const cd = e.clipboardData;
                const text = cd?.getData('text/plain') || '';
                const html = cd?.getData('text/html') || '';
                handlePlainInsert(text, html);
            };

            const onDrop = (e: DragEvent) => {
                e.preventDefault();
                // ставим каретку под курсор
                const rng = document.caretRangeFromPoint?.(e.clientX, e.clientY);
                if (rng) {
                    const sel = window.getSelection();
                    sel?.removeAllRanges();
                    sel?.addRange(rng);
                }
                const dt = e.dataTransfer;
                const text = dt?.getData('text/plain') || '';
                const html = dt?.getData('text/html') || '';
                handlePlainInsert(text, html);
            };

            el.addEventListener('beforeinput', onBeforeInput);
            el.addEventListener('paste', onPaste);
            el.addEventListener('drop', onDrop);

            return () => {
                el.removeEventListener('beforeinput', onBeforeInput);
                el.removeEventListener('paste', onPaste);
                el.removeEventListener('drop', onDrop);
            };
        }, []);

        /* ───────── ссылка-редактор ───────── */
        useEffect(() => {
            const el = editorRef.current;
            if (!el) return;

            const onClick = (e: MouseEvent) => {
                const target = e.target as HTMLElement;
                const a = target.closest('a');
                if (a && el.contains(a)) {
                    e.preventDefault();
                    e.stopPropagation();

                    const r = document.createRange();
                    r.selectNodeContents(a);
                    const sel = window.getSelection();
                    sel?.removeAllRanges();
                    sel?.addRange(r);

                    savedRangeRef.current = r.cloneRange();
                    setPendingUrl(a.getAttribute('href') || '');
                    setIsUrlModalOpen(true);
                }
            };

            el.addEventListener('click', onClick);
            return () => el.removeEventListener('click', onClick);
        }, []);

        const saveCurrentRange = () => {
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0) return;
            if (!editorRef.current?.contains(sel.anchorNode)) return;
            savedRangeRef.current = sel.getRangeAt(0).cloneRange();
        };

        const restoreRange = () => {
            const r = savedRangeRef.current;
            if (!r) return false;
            const sel = window.getSelection();
            if (!sel) return false;
            sel.removeAllRanges();
            sel.addRange(r);
            return true;
        };

        const openUrlModal = () => {
            saveCurrentRange();
            setPendingUrl('');
            setIsUrlModalOpen(true);
        };

        const handleInsertUrl = () => {
            if (!pendingUrl.trim()) {
                setIsUrlModalOpen(false);
                return;
            }
            if (!restoreRange()) {
                setIsUrlModalOpen(false);
                return;
            }
            let href = pendingUrl.trim();
            if (!/^https?:\/\//i.test(href)) href = 'https://' + href;
            wrapSelection('a', {href, target: '_blank', rel: 'noopener noreferrer'});
            setIsUrlModalOpen(false);
        };

        function wrapSelection(tagName: string, attrs: Record<string, string> = {}) {
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0) return;

            const range = sel.getRangeAt(0);
            const editor = editorRef.current;
            if (!editor) return;

            if (tagName.toLowerCase() === 'a') {
                const node = range.commonAncestorContainer;
                const el = (node.nodeType === Node.ELEMENT_NODE ? (node as Element) : (node.parentElement as Element | null));
                const existingA = el?.closest('a');

                if (existingA && editor.contains(existingA)) {
                    for (const [k, v] of Object.entries(attrs)) existingA.setAttribute(k, v);
                    editor.dispatchEvent(new Event('input'));
                    return;
                }
            }

            if (range.collapsed) return;

            editor.focus();

            const wrapper = document.createElement(tagName);
            for (const [k, v] of Object.entries(attrs)) wrapper.setAttribute(k, v);
            const fragment = range.extractContents();

            if (tagName.toLowerCase() === 'a') {
                fragment.querySelectorAll?.('a')?.forEach(a => {
                    const parent = a.parentNode!;
                    while (a.firstChild) parent.insertBefore(a.firstChild, a);
                    parent.removeChild(a);
                });
            }

            wrapper.appendChild(fragment);
            range.insertNode(wrapper);

            const newSel = window.getSelection();
            if (newSel) {
                const r2 = document.createRange();
                r2.setStartAfter(wrapper);
                r2.collapse(true);
                newSel.removeAllRanges();
                newSel.addRange(r2);
            }

            editor.dispatchEvent(new Event('input'));
        }

        const getUrlById = (id: string): string => {
            const found = emojis.find(e => e.custom_emoji_id === id);
            return found ? found.img_url : '';
        };

        /* начальный HTML один раз */
        useEffect(() => {
            if (editorRef.current) editorRef.current.innerHTML = initialContent;
            if (editorRef.current) handleInput();
            // eslint-disable-next-line react-hooks/exhaustive-deps
        }, []);

        const serialize = (el: HTMLDivElement) => {
            const clone = el.cloneNode(true) as HTMLDivElement;

            const html = el.innerHTML;

            const entities: MessageEntityDTO[] = [];
            let text = '';
            let offset = 0;

            const USING_FORMDATA = true;
            const NL = USING_FORMDATA ? '\r\n' : '\n';
            const NL_LEN = NL.length;

            function isBlankLineDiv(div: HTMLElement): boolean {
                if (div.tagName !== 'DIV' || div.parentElement !== clone) return false;
                const hasText = (div.textContent ?? '').replace(/\u00A0/g, ' ').trim().length > 0;
                if (hasText) return false;
                if (div.querySelector('img[data-custom-emoji-id],video[data-custom-emoji-id]')) return false;
                return !!div.querySelector('br');
            }

            function emitInline(node: Node) {
                node.childNodes.forEach((child) => {
                    if (child.nodeType === Node.TEXT_NODE) {
                        const s = (child as Text).data.replace(/\u00A0/g, ' ');
                        if (s) {
                            text += s;
                            offset += s.length;
                        }
                        return;
                    }

                    if (child.nodeType === Node.ELEMENT_NODE) {
                        const eln = child as HTMLElement;

                        if (
                            (eln.tagName === 'IMG' || eln.tagName === 'VIDEO') &&
                            eln.hasAttribute('data-custom-emoji-id')
                        ) {
                            const id = eln.getAttribute('data-custom-emoji-id')!;
                            text += RHINO;
                            entities.push({
                                type: 'custom_emoji',
                                offset,
                                length: RHINO_LEN,
                                custom_emoji_id: id
                            } as MessageEntityDTO);
                            offset += RHINO_LEN;
                            return;
                        }

                        if (eln.tagName === 'BR') {
                            text += NL;
                            offset += NL_LEN;
                            return;
                        }

                        let type: MessageEntityDTO['type'] | null = null;
                        if (eln.tagName === 'B') type = 'bold';
                        else if (eln.tagName === 'I') type = 'italic';
                        else if (eln.tagName === 'U') type = 'underline';
                        else if (eln.tagName === 'S') type = 'strikethrough';
                        else if (eln.tagName === 'A') type = 'text_link';
                        else if (eln.tagName === 'BLOCKQUOTE') type = 'blockquote';

                        const start = offset;
                        emitInline(eln);
                        const len = offset - start;

                        if (type && len > 0) {
                            const slice = text.slice(start, start + len);
                            const cleanLen = slice.replace(/\r?\n+$/g, '').length;
                            if (cleanLen > 0) {
                                const ent: MessageEntityDTO = {type, offset: start, length: cleanLen};
                                if (type === 'text_link') ent.url = eln.getAttribute('href') || undefined;
                                entities.push(ent);
                            }
                        }
                    }
                });
            }

            const blocks = Array.from(clone.children) as HTMLElement[];
            for (let i = 0; i < blocks.length; i++) {
                const div = blocks[i];

                if (isBlankLineDiv(div)) {
                    if (i < blocks.length - 1) {
                        text += NL;
                        offset += NL_LEN;
                    }
                    continue;
                }

                emitInline(div);

                if (i < blocks.length - 1) {
                    text += NL;
                    offset += NL_LEN;
                }
            }

            entities.sort((a, b) => a.offset - b.offset);
            const cleanEntities: MessageEntityDTO[] = entities.map((e) => {
                const base: MessageEntityDTO = {type: e.type, offset: e.offset, length: e.length};
                if (e.type === 'text_link' && e.url) base.url = e.url;
                if (e.type === 'custom_emoji' && e.custom_emoji_id) base.custom_emoji_id = e.custom_emoji_id;
                return base;
            });

            return {html, text, entities: cleanEntities};
        };

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
                        img.src = getUrlById(emojiId);
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

            const result = serialize(el);

            // тут же восстанавливаем все 🦏 → <img>
            restoreRhinos(el);

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

            const isVideo = emoji.format === 'video' || emoji.img_url.toLowerCase().endsWith('.webm');

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

            el.dispatchEvent(new Event('input'));
        };

        useImperativeHandle(ref, () => ({insertEmoji}), [insertEmoji]);

        return (
            <div className="relative">
                {/* ——— Панель кнопок форматирования ——— */}
                <div className="flex items-center mb-2 space-x-1">
                    <button type="button" onClick={() => wrapSelection('b')} className="px-2 py-1 border rounded">
                        <b>Ж</b></button>
                    <button type="button" onClick={() => wrapSelection('i')} className="px-2 py-1 border rounded">
                        <i>К</i></button>
                    <button type="button" onClick={() => wrapSelection('u')} className="px-2 py-1 border rounded">
                        <u>П</u></button>
                    <button type="button" onClick={() => wrapSelection('s')} className="px-2 py-1 border rounded">
                        <s>З</s></button>
                    <button
                        type="button"
                        onMouseDown={(e) => {
                            e.preventDefault();
                            openUrlModal();
                        }}
                        className="px-2 py-1 border rounded"
                    >🔗
                    </button>
                    <button type="button" onClick={() => wrapSelection('blockquote')}
                            className="px-2 py-1 border rounded" title="Цитата">❝❞
                    </button>
                </div>

                <div
                    ref={editorRef}
                    contentEditable
                    suppressContentEditableWarning
                    className="rich-editor border p-2 rounded min-h-[150px] focus:outline-none"
                    style={{whiteSpace: 'pre-wrap'}} // сохраняем \n как переносы, без <p>
                />

                {isUrlModalOpen && (
                    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
                        <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md relative">
                            <button onClick={() => setIsUrlModalOpen(false)}
                                    className="absolute top-2 right-2 text-gray-500 hover:text-gray-700">✕
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
                            <button onClick={handleInsertUrl}
                                    className="w-full py-2 bg-brand text-white rounded hover:bg-brand transition">
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
