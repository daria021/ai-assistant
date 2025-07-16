import React, {useEffect, useRef, useState} from 'react'
import type {Emoji, MessageEntityDTO} from '../services/api'
import {EmojiPicker} from './EmojiPicker'

export interface RichEditorProps {
    /** Список платных эмодзи из БД */
    emojis: Emoji[]
    /** Начальное HTML-содержимое */
    initialContent?: string
    /**
     * Вызывается при каждом изменении:
     * - html: текущее innerHTML
     * - text: textContent без HTML
     * - entities: массив объектов вида { type:'custom_emoji', offset, length:2, custom_emoji_id }
     */
    onChange: (payload: {
        html: string
        text: string
        entities: MessageEntityDTO[]
    }) => void
}

/**
 * Простой WYSIWYG-редактор на contentEditable,
 * с кнопкой для открытия пикера платных эмодзи.
 *
 * - Уникальные ключи React всегда берутся из emoji.custom_emoji_id
 * - Никаких random-ключей и uuid-генерации внутри render’а
 */
export const RichEditor: React.FC<RichEditorProps> = ({
                                                          emojis,
                                                          initialContent = '',
                                                          onChange,
                                                      }) => {
    const editorRef = useRef<HTMLDivElement>(null);
    const [pickerOpen, setPickerOpen] = useState(false);

    useEffect(() => {
        if (editorRef.current) {
            editorRef.current.innerHTML = initialContent;
        }
    }, []);

    // При монтировании и каждом вводе собираем html/text/entities и зовём onChange
    useEffect(() => {
        const el = editorRef.current;
        if (!el) return;

        const handleInput = () => {
            const html = el.innerHTML;
            const text = el.textContent || '';

            // Собираем все вставленные <img data-custom-emoji-id="...">
            const entities: MessageEntityDTO[] = [];
            el.querySelectorAll<HTMLImageElement>('img[data-custom-emoji-id]').forEach(img => {
                const id = img.dataset.customEmojiId!;
                // позиция в plain-тексте: находим первый вхождений alt-текста
                const offset = text.indexOf(img.alt);
                entities.push({
                    type: 'custom_emoji',
                    offset,
                    length: 2,
                    custom_emoji_id: id,
                });
            });

            onChange({html, text, entities});
        }

        el.addEventListener('input', handleInput);
        return () => el.removeEventListener('input', handleInput);
    }, [onChange])

    // Вставить выбранный emoji (объект из props) в позицию курсора
    const insertEmoji = (emoji: Emoji) => {
        const sel = window.getSelection();
        if (!sel || !sel.rangeCount) return;
        const range = sel.getRangeAt(0);
        range.deleteContents();

        // Создаём <img> c данными для сериализации
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

        // Форсируем input-событие, чтобы onChange сработал сразу
        editorRef.current?.dispatchEvent(new Event('input'));
    }

    return (
        <div className="relative">
            {/* Тулбар с кнопкой эмодзи */}
            <div className="flex items-center mb-2">
                <button
                    type="button"
                    onClick={() => setPickerOpen(v => !v)}
                    className="px-2 py-1 rounded hover:bg-gray-200"
                >
                    😊
                </button>
            </div>

            {/* Редактируемый блок */}
            <div
                ref={editorRef}
                contentEditable
                suppressContentEditableWarning
                className="border p-2 rounded min-h-[150px] focus:outline-none"
            />

            {/* Пикер эмодзи */}
            {pickerOpen && (
                <EmojiPicker
                    emojis={emojis}
                    onSelect={emoji => {
                        insertEmoji(emoji)
                        setPickerOpen(false)
                    }}
                />
            )}
        </div>
    )
}
