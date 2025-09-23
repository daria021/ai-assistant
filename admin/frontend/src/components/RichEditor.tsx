import { forwardRef, useEffect, useImperativeHandle, useRef, useState} from 'react';
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

        // 1) HTML -> plain text без эмбедов/кастом-эмодзи (Unicode-эмодзи остаются)
        function htmlToPlainStrict(html: string): string {
            const tmp = document.createElement('div');
            tmp.innerHTML = html;

            // 1) выбрасываем потенциальные кастом-эмодзи/эмбеды
            tmp.querySelectorAll(`
    img,
    video,
    tg-emoji,
    picture, source, canvas, iframe, object, embed, svg
  `).forEach(n => n.remove());

            // 2) берём видимый текст
            return (tmp as HTMLElement).innerText.replace(/\u00A0/g, ' ');
        }

        // 2) Нормализация текста: сохраняем абзацы, вычищаем «квадраты»
        function normalizePastedText(raw: string): string {
            return raw
                .replace(/\u00A0/g, ' ')
                .replace(/\r\n?/g, '\n')
                .replace(/[ \t]+\n/g, '\n')
                // eslint-disable-next-line no-misleading-character-class
                .replace(/[\uFFFC\uFFFD\uFE0E\uFE0F]/g, '') // Object/Replacement + variation selectors
                .replace(/[\uE000-\uF8FF]/g, '')
                .replace(/^\n+|\n+$/g, '')
                .replace(/\n{5,}/g, '\n\n\n\n')
                .replace(/<([a-z][\w-]*)\b[^>]*>🦏<\/\1>/gi, ' ');
        }

        // 3) Вставка только текста (никаких execCommand; создаём Text + <br>)
        const insertPlainTextAtSelection = (text: string) => {
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0) return;

            const range = sel.getRangeAt(0);
            range.deleteContents();

            const frag = document.createDocumentFragment();
            const lines = text.split('\n'); // уже нормализовано
            lines.forEach((line, i) => {
                frag.appendChild(document.createTextNode(line));
                if (i < lines.length - 1) frag.appendChild(document.createElement('br'));
            });

            range.insertNode(frag);                               // MDN: Range.insertNode
            sel.removeAllRanges();
            const end = document.createRange();
            end.selectNodeContents(editorRef.current as HTMLDivElement);
            end.collapse(false);
            sel.addRange(end);
            editorRef.current?.dispatchEvent(new Event('input'));
        };

        useEffect(() => {
            const el = editorRef.current;
            if (!el) return;

            const handlePlainInsert = (text?: string, html?: string) => {
                // ВСЕГДА предпочитаем HTML, потому что умеем вырезать кастом-эмодзи из него
                const raw = html && html.length ? htmlToPlainStrict(html) : (text || '');
                const clean = normalizePastedText(raw);
                if (clean) insertPlainTextAtSelection(clean);
            };

            const onDragOver = (e: DragEvent) => {
                e.preventDefault();
            };

            // beforeinput (раньше нативной вставки, работает и для contenteditable)
            const onBeforeInput = (e: InputEvent & { dataTransfer?: DataTransfer | null }) => {
                const t = e.inputType; // MDN: InputEvent.inputType
                if (t === 'insertFromPaste' || t === 'insertFromPasteAsQuotation' || t === 'insertFromDrop') {
                    if (e.cancelable) e.preventDefault();
                    e.stopPropagation();
                    const dt = e.dataTransfer ?? null; // MDN: InputEvent.dataTransfer
                    const text = dt?.getData('text/plain') ?? '';
                    const html = dt?.getData('text/html') ?? '';
                    handlePlainInsert(text, html);
                }
            };

            // Классический paste (ClipboardEvent.clipboardData)
            const onPaste = (e: ClipboardEvent) => {
                const cd = e.clipboardData;
                if (cd && (cd.files?.length ?? 0) > 0) {
                    e.preventDefault();
                    e.stopPropagation();
                    return; // не вставляем файлы/картинки
                }
                e.preventDefault();
                e.stopPropagation();
                const text = cd?.getData('text/plain') || '';
                const html = cd?.getData('text/html') || '';
                handlePlainInsert(text, html);
            };

            const onDrop = (e: DragEvent) => {
                // если тянут файл/картинку — блокируем
                if (e.dataTransfer && [...(e.dataTransfer.items || [])].some(i => i.kind === 'file')) {
                    e.preventDefault();
                    e.stopPropagation();
                    return;
                }
                e.preventDefault();
                e.stopPropagation();
                // ставим каретку и вставляем только текст:
                const anyDoc = document;
                const rng: Range | null =
                    (anyDoc.caretRangeFromPoint && anyDoc.caretRangeFromPoint(e.clientX, e.clientY)) || null;
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

            // Документ-уровневый запасной перехват (если кто-то мешает на элементе)
            const onDocPasteCapture = (e: ClipboardEvent) => {
                const active = document.activeElement;
                if (!active || !el.contains(active)) return;
                e.preventDefault();
                e.stopPropagation();
                const cd = e.clipboardData;
                const text = cd?.getData('text/plain') || '';
                const html = cd?.getData('text/html') || '';
                handlePlainInsert(text, html);
            };

            el.addEventListener('dragover', onDragOver, {capture: true});
            el.addEventListener('beforeinput', onBeforeInput, {capture: true}); // MDN/W3C: beforeinput
            el.addEventListener('paste', onPaste, {capture: true});             // MDN: ClipboardEvent.clipboardData
            el.addEventListener('drop', onDrop, {capture: true});

            document.addEventListener('paste', onDocPasteCapture, {capture: true});

            return () => {
                el.removeEventListener('dragover', onDragOver, {capture: true});
                el.removeEventListener('beforeinput', onBeforeInput, {capture: true});
                el.removeEventListener('paste', onPaste, {capture: true});
                el.removeEventListener('drop', onDrop, {capture: true});
                document.removeEventListener('paste', onDocPasteCapture, {capture: true});
            };
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
            saveCurrentRange();         // <- сохраняем выделение
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
            }  // <- возвращаем выделение в редактор
            let href = pendingUrl.trim();
            if (!/^https?:\/\//i.test(href)) href = 'https://' + href;  // легкая нормализация
            wrapSelection('a', {href, target: '_blank', rel: 'noopener noreferrer'});
            setIsUrlModalOpen(false);
        };

        const closeUrlModal = () => setIsUrlModalOpen(false);

        // очередь ID для восстановления эмодзи
        function wrapSelection(tagName: string, attrs: Record<string, string> = {}) {
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0) return;

            const range = sel.getRangeAt(0);
            const editor = editorRef.current;
            if (!editor) return;

            // Если работаем с ссылкой — сначала проверим, внутри ли мы уже <a>
            if (tagName.toLowerCase() === 'a') {
                const node = range.commonAncestorContainer;
                const el = (node.nodeType === Node.ELEMENT_NODE
                    ? (node as Element)
                    : (node.parentElement as Element | null));
                const existingA = el?.closest('a');

                if (existingA && editor.contains(existingA)) {
                    // просто обновляем href/атрибуты у существующей ссылки
                    for (const [k, v] of Object.entries(attrs)) existingA.setAttribute(k, v);
                    editor.dispatchEvent(new Event('input'));
                    return;
                }
            }

            if (range.collapsed) return;

            editor.focus();

            // создаём новый wrapper и переносим выделение внутрь
            const wrapper = document.createElement(tagName);
            for (const [k, v] of Object.entries(attrs)) wrapper.setAttribute(k, v);
            const fragment = range.extractContents();

            // На всякий случай убираем вложенные <a> внутри фрагмента (если были)
            if (tagName.toLowerCase() === 'a') {
                fragment.querySelectorAll?.('a')?.forEach(a => {
                    const parent = a.parentNode!;
                    while (a.firstChild) parent.insertBefore(a.firstChild, a);
                    parent.removeChild(a);
                });
            }

            wrapper.appendChild(fragment);
            range.insertNode(wrapper);

            // ставим курсор после wrapper
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

        const serialize = (el: HTMLDivElement, options: { mutateDom?: boolean } = {}) => {
            const { mutateDom = false } = options;
            const clone = el.cloneNode(true) as HTMLDivElement;

            // 0.1) Сначала группируем в DIV-блоки
            (function ensureDivBlocks(root: HTMLElement) {
                const nodes = Array.from(root.childNodes);
                const frag = document.createDocumentFragment();
                let cur: HTMLDivElement | null = null;

                for (const n of nodes) {
                    if (n.nodeType === Node.ELEMENT_NODE && (n as HTMLElement).tagName === 'DIV') {
                        cur = null;
                        frag.appendChild(n);             // готовый блок остаётся как есть
                    } else {
                        if (!cur) {                      // начинаем новый искусственный блок
                            cur = document.createElement('div');
                            frag.appendChild(cur);
                        }
                        cur.appendChild(n);              // переносим IMG/VIDEO/BR/текст внутрь блока
                    }
                }
                root.innerHTML = '';
                root.appendChild(frag);
            })(clone);

            // 0) Теперь нормализуем внутри каждого DIV-блока
            clone.normalize();

            // Перерисовка DOM может сбивать каретку — делаем её опциональной
            if (mutateDom) {
                el.innerHTML = clone.innerHTML;
            }

            idsRef.current.length = 0;

            const html = mutateDom ? el.innerHTML : clone.innerHTML;
            const entities: MessageEntityDTO[] = [];
            let text = '';
            let offset = 0;

            const USING_FORMDATA = true;
            const NL = USING_FORMDATA ? '\r\n' : '\n';
            const NL_LEN = NL.length;

            function blankBreaksCount(div: HTMLElement): number {
                if (div.tagName !== 'DIV' || div.parentElement !== clone) return 0;

                const hasEmojis = div.querySelector('img[data-custom-emoji-id],video[data-custom-emoji-id]');
                if (hasEmojis) return 0; // Если есть эмодзи, не пустой

                // Проверяем все текстовые узлы в блоке
                const textNodes = Array.from(div.childNodes).filter(node =>
                    node.nodeType === Node.TEXT_NODE
                ) as Text[];

                const hasNonEmptyText = textNodes.some(node => {
                    const text = node.data.replace(/\u00A0/g, ' ').trim();
                    return text.length > 0;
                });

                if (hasNonEmptyText) return 0; // Есть непустой текст

                // Проверяем, есть ли пробельные текстовые узлы
                const hasWhitespaceNodes = textNodes.some(node => /\s/.test(node.data));

                if (hasWhitespaceNodes) {
                    return 1; // Есть пробельные узлы - считаем как пустую строку
                }

                // Считаем <br> элементы для остальных случаев
                return div.querySelectorAll('br').length;
              }              

            // ← ТВОЙ emitInline, но с фильтром пробельных узлов
            function emitInline(node: Node) {
                if (node.nodeType === Node.TEXT_NODE) {
                    const raw = (node as Text).data.replace(/\u00A0/g, ' ');
                    if (/\S/.test(raw)) {             // ← фильтр: только если есть непробельные символы
                        text += raw;
                        offset += raw.length;
                    }
                    return;
                }

                if (node.nodeType === Node.ELEMENT_NODE) {
                    const eln = node as HTMLElement;

                    if ((eln.tagName === 'IMG' || eln.tagName === 'VIDEO') && eln.hasAttribute('data-custom-emoji-id')) {
                        const id = eln.getAttribute('data-custom-emoji-id')!;
                        idsRef.current.push(id);
                        text += RHINO;
                        entities.push({
                            type: 'custom_emoji',
                            offset,
                            length: RHINO_LEN,
                            custom_emoji_id: id,
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
                    eln.childNodes.forEach((child) => emitInline(child));
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
            }

            // 2) теперь корень гарантированно состоит из DIV-блоков → твоя логика переносов не меняется
            const blocks = Array.from(clone.children) as HTMLElement[];
for (let i = 0; i < blocks.length; i++) {
  const div = blocks[i];

  const brCount = blankBreaksCount(div);     // ← счётчик пустых строк внутри блока
  if (brCount > 0) {
    // Добавляем столько переносов, сколько <br> внутри DIV.
    // Если хочешь ограничить, например максимумом 3, сделай:
    // const n = Math.min(brCount, 3);
    const n = brCount;

    if (i < blocks.length - 1) {
      for (let k = 0; k < n; k++) {
        text += NL;
        offset += NL_LEN;
      }
    }
    continue;
  }

  const before = offset;
  emitInline(div);

  // Перенос между непустыми блоками — только если блок не закончился на <br>
  if (i < blocks.length - 1 && offset > before && !text.endsWith(NL)) {
    text += NL;
    offset += NL_LEN;
  }
}


            entities.sort((a, b) => a.offset - b.offset);
            const cleanEntities = entities.map((e) => {
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
                if (node.nodeValue?.includes(RHINO)) textNodes.push(node);
            }

            textNodes.forEach(textNode => {
                const parts = textNode.nodeValue!.split(RHINO);
                const frag = document.createDocumentFragment();

                parts.forEach((part, idx) => {
                    frag.appendChild(document.createTextNode(part));
                    if (idx < parts.length - 1) {
                        const emojiId = idsRef.current.shift()!;
                        if (emojiId) {
                            const img = document.createElement('img');
                            img.setAttribute('data-custom-emoji-id', emojiId);
                            img.src = getUrlById(emojiId);  // ваша функция получения URL по id
                            img.width = img.height = 24;
                            img.style.display = 'inline-block';
                            img.style.verticalAlign = 'middle';
                            frag.appendChild(img);
                        }
                    }
                });

                textNode.parentNode!.replaceChild(frag, textNode);
            });
        }

        /* ---------- единый обработчик input ---------- */
        const handleInput = () => {
            const el = editorRef.current;
            if (!el) return;

            // сериализуем без мутации DOM, чтобы не терять каретку
            const result = serialize(el, { mutateDom: false });

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
                        onMouseDown={(e) => {
                            e.preventDefault();
                            openUrlModal();
                        }}
                        className="px-2 py-1 border rounded"
                    >
                        🔗
                    </button>

                    {/* ← новая кнопка для цитаты */}
                    <button
                        type="button"
                        onClick={() => wrapSelection('blockquote')}
                        className="px-2 py-1 border rounded"
                        title="Цитата"
                    >
                        ❝❞
                    </button>
                </div>

                <div
                    ref={editorRef}
                    contentEditable
                    suppressContentEditableWarning
                    className="rich-editor border p-2 rounded min-h-[150px] focus:outline-none"
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
