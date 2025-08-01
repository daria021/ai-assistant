import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react'
import type { Emoji, MessageEntityDTO } from '../services/api'

/* ----- наружу отдаём только insertEmoji ----- */
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
  ({ initialContent = '', onChange }, ref) => {
    const editorRef = useRef<HTMLDivElement>(null)

    /* ставим начальный HTML один раз */
    useEffect(() => {
      if (editorRef.current) editorRef.current.innerHTML = initialContent
    }, [])

    /* ---------- вытаскиваем entities ---------- */
    const extractEntities = (el: HTMLDivElement) => {
      const entities: MessageEntityDTO[] = []
      let idx = 0

      const walker = document.createTreeWalker(
        el,
        NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
        {
          acceptNode(node) {
            if (node.nodeType === Node.TEXT_NODE) return NodeFilter.FILTER_ACCEPT
            if (
              node.nodeType === NodeFilter.SHOW_ELEMENT &&
              (node as Element).matches(
                'img[data-custom-emoji-id],video[data-custom-emoji-id]',
              )
            )
              return NodeFilter.FILTER_ACCEPT
            return NodeFilter.FILTER_SKIP
          },
        },
      )

      while (walker.nextNode()) {
        const node = walker.currentNode
        if (node.nodeType === Node.TEXT_NODE) {
          idx += (node.textContent ?? '').length
        } else {
          const elNode = node as HTMLElement
          const id = elNode.dataset.customEmojiId!
          entities.push({
            type: 'custom_emoji',
            offset: idx,
            length: 2,
            custom_emoji_id: id,
          } as MessageEntityDTO)
          idx += 2
        }
      }

      return entities
    }

    /* ---------- хук onInput ---------- */
    useEffect(() => {
      const el = editorRef.current
      if (!el) return
      const handleInput = () => {
        const entities = extractEntities(el)

        const clone = el.cloneNode(true) as HTMLDivElement
        clone
          .querySelectorAll(
            'img[data-custom-emoji-id],video[data-custom-emoji-id]',
          )
          .forEach(node => {
            const rhino = document.createTextNode('🦏')
            node.parentNode?.replaceChild(rhino, node)
          })

        const html = clone.innerHTML
        const text = clone.textContent || ''
        onChange({ html, text, entities })
      }
      el.addEventListener('input', handleInput)
      return () => el.removeEventListener('input', handleInput)
    }, [onChange])

    /* ---------- логика вставки ---------- */
    const insertEmoji = (emoji: Emoji) => {
      const el = editorRef.current
      if (!el) return

      let sel = window.getSelection()
      const inEditor =
        sel && sel.rangeCount > 0 && el.contains(sel.getRangeAt(0).startContainer)

      if (!inEditor) {
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

      const isVideo =
        emoji.format === 'video' ||
        emoji.img_url.toLowerCase().endsWith('.webm')

      const node: HTMLElement = isVideo
        ? (() => {
            const v = document.createElement('video')
            v.src = emoji.img_url
            v.loop = true
            v.muted = true
            v.autoplay = true
            v.playsInline = true
            v.width = v.height = 24
            return v
          })()
        : (() => {
            const i = document.createElement('img')
            i.src = emoji.img_url
            i.alt = emoji.name
            i.width = i.height = 24
            return i
          })()

      node.setAttribute('data-custom-emoji-id', emoji.custom_emoji_id)
      node.style.display = 'inline-block'
      node.style.verticalAlign = 'middle'

      range.insertNode(node)
      range.setStartAfter(node)
      sel.removeAllRanges()
      sel.addRange(range)

      /* триггерим input */
      el.dispatchEvent(new Event('input'))
    }

    /* отдаём наружу */
    useImperativeHandle(ref, () => ({ insertEmoji }), [insertEmoji])

    return (
      <div className="relative">
        <div
          ref={editorRef}
          contentEditable
          suppressContentEditableWarning
          className="border p-2 rounded min-h-[150px] focus:outline-none"
        />
      </div>
    )
  },
)
RichEditor.displayName = 'RichEditor'
