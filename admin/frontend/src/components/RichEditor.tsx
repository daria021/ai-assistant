import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState
} from 'react'
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

    // onChange‑хук
    useEffect(() => {
      const el = editorRef.current
      if (!el) return
      const handleInput = () => {
        const html = el.innerHTML
        const text = el.textContent || ''
        const entities: MessageEntityDTO[] = []
        el.querySelectorAll<HTMLImageElement>('img[data-custom-emoji-id]')
          .forEach(img => {
            const id = img.dataset.customEmojiId!
            const offset = text.indexOf(img.alt)
            entities.push({
              type: 'custom_emoji',
              offset,
              length: 2,
              custom_emoji_id: id
            })
          })
        onChange({html, text, entities})
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
        {/* если не хотите встроенную кнопку, можно её убрать */}
        <div className="flex items-center mb-2">
          <button
            type="button"
            onClick={() => setPickerOpen(v => !v)}
            className="px-2 py-1 rounded hover:bg-gray-200"
          >
            😊
          </button>
        </div>

        <div
          ref={editorRef}
          contentEditable
          suppressContentEditableWarning
          className="border p-2 rounded min-h-[150px] focus:outline-none"
        />

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
)
RichEditor.displayName = 'RichEditor'
