import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
} from 'react';
import type { Emoji, MessageEntityDTO } from '../services/api';

/* ───────── константы ───────── */
const RHINO = '🦏';          // плейсхолдер
const RHINO_LEN = 2;         // 1 юникод-символ = 2 UTF-16 code units

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
  ({ initialContent = '', onChange }, ref) => {
    const editorRef = useRef<HTMLDivElement>(null);

    /* ставим начальный HTML один раз */
    useEffect(() => {
      if (editorRef.current) editorRef.current.innerHTML = initialContent;
      // сразу пробрасываем initialContent наружу
      if (editorRef.current) handleInput();
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    /* ---------- универсальная сериализация ---------- */
    const serialize = (el: HTMLDivElement) => {
      // 1. Клонируем, чтобы не портить реальный DOM
      const clone = el.cloneNode(true) as HTMLDivElement;

      // 2. Собираем custom_emoji_id в порядке обхода
      const ids: string[] = [];
      clone
        .querySelectorAll(
          'img[data-custom-emoji-id],video[data-custom-emoji-id]',
        )
        .forEach(node => {
          const id = (node as HTMLElement).dataset.customEmojiId;
          if (id) ids.push(id);
          // меняем <img>/<video> на 🦏
          node.replaceWith(document.createTextNode(RHINO));
        });

      // 3. Получаем итоговые строки
      const html = clone.innerHTML;
      const text = clone.innerText; // именно innerText → учитывает \n так же, как Telegram

      // 4. Строим entities по найденным 🦏
      const entities: MessageEntityDTO[] = [];
      const rx = new RegExp(RHINO, 'g');
      let match: RegExpExecArray | null;
      let i = 0;
      while ((match = rx.exec(text))) {
        entities.push({
          type: 'custom_emoji',
          offset: match.index,
          length: RHINO_LEN,
          custom_emoji_id: ids[i++] ?? '',
        } as MessageEntityDTO);
      }

      return { html, text, entities };
    };

    /* ---------- единый обработчик input ---------- */
    const handleInput = () => {
      const el = editorRef.current;
      if (!el) return;
      onChange(serialize(el));
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
    useImperativeHandle(ref, () => ({ insertEmoji }), [insertEmoji]);

    return (
      <div className="relative">
        <div
          ref={editorRef}
          contentEditable
          suppressContentEditableWarning
          className="border p-2 rounded min-h-[150px] focus:outline-none"
        />
      </div>
    );
  },
);
RichEditor.displayName = 'RichEditor';
