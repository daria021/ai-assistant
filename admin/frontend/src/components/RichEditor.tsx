import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react';
import type { Emoji, MessageEntityDTO } from '../services/api';
import { EmojiPicker } from './EmojiPicker';

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
  ({ emojis, initialContent = '', onChange }, ref) => {
    const editorRef = useRef<HTMLDivElement>(null);
    const [pickerOpen, setPickerOpen] = useState(false);

    // 1) Инициализация контента один раз
    useEffect(() => {
      if (editorRef.current) {
        editorRef.current.innerHTML = initialContent;
      }
    }, [initialContent]);

    // 2) Собираем сущности custom_emoji через TreeWalker
    const extractEntities = (el: HTMLDivElement) => {
      const entities: MessageEntityDTO[] = [];
      let idx = 0;

      const walker = document.createTreeWalker(
        el,
        NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
        {
          acceptNode(node) {
            // принимаем только текст и <img data-custom-emoji-id>
            if (node.nodeType === NodeFilter.SHOW_TEXT) return NodeFilter.FILTER_ACCEPT;
            if (
              node.nodeType === NodeFilter.SHOW_ELEMENT &&
              (node as Element).matches('img[data-custom-emoji-id]')
            )
              return NodeFilter.FILTER_ACCEPT;
            return NodeFilter.FILTER_SKIP;
          },
        }
      );

      while (walker.nextNode()) {
        const node = walker.currentNode;
        if (node.nodeType === Node.TEXT_NODE) {
          idx += (node.textContent ?? '').length;
        } else {
          const img = node as HTMLImageElement;
          const id = img.dataset.customEmojiId!;
          entities.push({
            type: 'custom_emoji',
            offset: idx,
            length: 2,
            custom_emoji_id: id,
          });
          idx += 2;
        }
      }

      return entities;
    };

    // 3) Хук onChange: слушаем ввод и отдаем html/text/entities
    useEffect(() => {
      const el = editorRef.current;
      if (!el) return;

      const handleInput = () => {
        // получаем сущности по оригинальному DOM
        const entities = extractEntities(el);

        // клонируем, заменяем картинки на 🦏 для html/text
        const clone = el.cloneNode(true) as HTMLDivElement;
        clone.querySelectorAll('img[data-custom-emoji-id]').forEach((img) => {
          img.replaceWith(document.createTextNode('🦏'));
        });

        const html = clone.innerHTML;
        const text = clone.textContent || '';

        onChange({ html, text, entities });
      };

      el.addEventListener('input', handleInput);
      return () => void el.removeEventListener('input', handleInput);
    }, [onChange]);

    // 4) Функция вставки: вставляем <img> как прежде
    const insertEmoji = (emoji: Emoji) => {
      const el = editorRef.current;
      if (!el) return;

      let sel = window.getSelection();
      const inEditor =
        sel &&
        sel.rangeCount > 0 &&
        el.contains(sel.getRangeAt(0).startContainer);

      // если курсор вне редактора — фокусируем в конец
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

      // удаляем выделение и вставляем картинку
      range.deleteContents();
      const img = document.createElement('img');
      img.src = emoji.img_url;
      img.alt = emoji.name;
      img.width = img.height = 24;
      img.setAttribute('data-custom-emoji-id', emoji.custom_emoji_id);
      img.style.display = 'inline-block';
      img.style.verticalAlign = 'middle';

      range.insertNode(img);
      range.setStartAfter(img);
      sel.removeAllRanges();
      sel.addRange(range);

      // триггерим input, чтобы запустился onChange
      el.dispatchEvent(new Event('input'));
    };

    // 5) Выносим insertEmoji наружу через ref
    useImperativeHandle(ref, () => ({ insertEmoji }), [insertEmoji]);

    return (
      <div className="relative">
        {/* Кнопка открытия попапа */}
        <button
          type="button"
          onClick={() => setPickerOpen((o) => !o)}
          className="absolute top-2 right-2 z-30 px-2 py-1 rounded hover:bg-gray-200"
        >
          😊
        </button>

        {/* Редактируемая область */}
        <div
          ref={editorRef}
          contentEditable
          suppressContentEditableWarning
          className="border p-2 rounded min-h-[150px] focus:outline-none"
        />

        {/* Сам попап — приклеен к этому же контейнеру */}
        {pickerOpen && (
          <div className="absolute top-full left-0 mt-1 w-80 max-h-64 overflow-auto bg-white shadow-lg rounded z-50">
            <EmojiPicker
              emojis={emojis}
              onSelect={(emoji) => {
                insertEmoji(emoji);
                setPickerOpen(false);
              }}
            />
          </div>
        )}
      </div>
    );
  }
);

RichEditor.displayName = 'RichEditor';
