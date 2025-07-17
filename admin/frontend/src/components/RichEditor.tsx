import {forwardRef, useEffect, useImperativeHandle, useRef, useState} from 'react'
import type {Emoji, MessageEntityDTO} from '../services/api'
import {EmojiPicker} from './EmojiPicker'

// описываем, что мы отдадим наружу
export type RichEditorHandle = {
    insertEmoji: (emoji: Emoji) => void
}

export interface RichEditorProps {
    emojis: Emoji[]
    initialContent?: string
    onChange: (payload: {
        html: string
        text: string
        entities: MessageEntityDTO[]
    }) => void
}

export const RichEditor = forwardRef<RichEditorHandle, RichEditorProps>(
    ({emojis, initialContent = '', onChange}, ref) => {
        const editorRef = useRef<HTMLDivElement>(null)
        const [pickerOpen, setPickerOpen] = useState(false)

        // замещаем initialContent ОДИН раз
        useEffect(() => {
            if (editorRef.current) {
                editorRef.current.innerHTML = initialContent
            }
        }, [])

        const extractEntities = (el: HTMLDivElement) => {
            const entities: MessageEntityDTO[] = [];
            let idx = 0;

            const walker = document.createTreeWalker(
                el,
                NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
                {
                    acceptNode(node) {
                        if (node.nodeType === NodeFilter.SHOW_TEXT) return NodeFilter.FILTER_ACCEPT;
                        if (
                            node.nodeType === NodeFilter.SHOW_ELEMENT &&
                            (node as Element).matches('img[data-custom-emoji-id]')
                        ) return NodeFilter.FILTER_ACCEPT;
                        return NodeFilter.FILTER_SKIP;
                    },
                },
            )

            while (walker.nextNode()) {
                const node = walker.currentNode;
                console.log(node);
                if (node.nodeType === Node.TEXT_NODE) {
                    console.log("text node");
                    console.log("idx: ", idx);
                    console.log(node.textContent);
                    idx += (node.textContent ?? '').length;
                    console.log("new idx: ", idx);
                } else {
                    const img = node as HTMLImageElement;
                    const id = img.dataset.customEmojiId!;
                    console.log(`image node with id ${id} at ${idx}`);
                    const entity = {
                        type: 'custom_emoji',
                        offset: idx,
                        length: 2,
                        custom_emoji_id: id,
                    };
                    console.log(entity);
                    entities.push(entity as MessageEntityDTO);
                    idx += 2;
                    console.log("new idx: ", idx);
                }
            }

            return entities
        }


        // onChange‑хук
        useEffect(() => {
            const el = editorRef.current;
            if (!el) return;
            const handleInput = () => {
                // const html = el.innerHTML;
                // const text = el.textContent || '';
                const entities = extractEntities(el);
                const clone = el.cloneNode(true) as HTMLDivElement
                clone
                    .querySelectorAll('img[data-custom-emoji-id]')
                    .forEach(img => {
                        const rhino = document.createTextNode('🦏')
                        img.parentNode?.replaceChild(rhino, img)
                    })

                // 4. Собираем чистый HTML и текст из клона
                const html = clone.innerHTML
                const text = clone.textContent || ''
                onChange({html, text, entities});
            }
            el.addEventListener('input', handleInput)
            return () => el.removeEventListener('input', handleInput)
        }, [onChange])

        // вот наша логика вставки
        const insertEmoji = (emoji: Emoji) => {
            const el = editorRef.current
            if (!el) return

            let sel = window.getSelection()
            const inEditor =
                sel &&
                sel.rangeCount > 0 &&
                el.contains(sel.getRangeAt(0).startContainer)

            if (!inEditor) {
                // фокусируем в конец, если курсор не в редакторе
                el.focus()
                const r = document.createRange()
                r.selectNodeContents(el)
                r.collapse(false)
                sel?.removeAllRanges()
                sel?.addRange(r)
            }

            sel = window.getSelection()
            if (!sel || !sel.rangeCount) return
            const range = sel.getRangeAt(0)
            range.deleteContents()

            const img = document.createElement('img')
            img.src = emoji.img_url
            img.alt = emoji.name
            img.width = img.height = 24
            img.setAttribute('data-custom-emoji-id', emoji.custom_emoji_id)
            img.style.display = 'inline-block'
            img.style.verticalAlign = 'middle'

            range.insertNode(img)
            range.setStartAfter(img)
            sel.removeAllRanges()
            sel.addRange(range)

            // триггерим input для onChange
            el.dispatchEvent(new Event('input'))
        }


        // «выливаем» insertEmoji наружу
        useImperativeHandle(ref, () => ({insertEmoji}), [insertEmoji])

        return (
            <div className="relative">

                <div
                    ref={editorRef}
                    contentEditable
                    suppressContentEditableWarning
                    className="border p-2 rounded min-h-[150px] focus:outline-none"
                />

                {pickerOpen && (
                    <div className="absolute top-full left-0 mt-1 z-20">
                        <EmojiPicker
                            emojis={emojis}
                            onSelect={emoji => {
                                insertEmoji(emoji)
                                setPickerOpen(false)
                            }}
                        />
                    </div>
                )}
            </div>
        )
    }
)
RichEditor.displayName = 'RichEditor'
