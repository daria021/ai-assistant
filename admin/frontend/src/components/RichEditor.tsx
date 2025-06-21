import {EditorContent, Extension, useEditor} from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Suggestion from '@tiptap/suggestion'
import type {Editor} from '@tiptap/core'
import {Node} from '@tiptap/core'
import type {Emoji} from '../services/api'
import type { Node as PMNode } from '@tiptap/pm/model'
import {useEffect} from "react";


/* ── типы ─────────────────────────────────────── */
interface EmojiAttrs {
    id: string
    label: string
    src: string
    custom_emoji_id: string
}

export interface EmojiEntity {
    type: 'custom_emoji'
    offset: number
    length: 2
    custom_emoji_id: string
}

interface Props {
    emojis: Emoji[]
    initialContent?: string
    onChange: (p: { html: string; text: string; entities: EmojiEntity[] }) => void
}


const EmojiNode = Node.create({
    name: 'emoji',
    inline: true,
    group: 'inline',
    atom: true,

    addAttributes() {
        return {
            id: {default: ''},
            src: {default: ''},
            name: {default: ''},
            custom_emoji_id: {default: ''}
        }
    },

    /* — парсинг из HTML (paste/SSR) — */
    parseHTML() {
        return [
            {tag: 'img[data-emoji-id]'},
            {tag: 'video[data-emoji-id]'},
        ]
    },

    /* — HTML-экспорт (editor.getHTML()) — */
    renderHTML({node}) {
        const src = node.attrs.src as string
        return src.endsWith('.webm')
            ? ['video', {
                'data-emoji-id': node.attrs.id,
                src,
                width: '24',
                height: '24',
                autoplay: 'true',
                loop: 'true',
                muted: 'true',
                style: 'display:inline-block;vertical-align:middle',
            }]
            : ['img', {
                'data-emoji-id': node.attrs.id,
                src,
                alt: node.attrs.name,
                width: '24',
                height: '24',
                style: 'display:inline-block;vertical-align:middle',
            }]
    },


    /* — DOM-рендер внутри редактора — */
    addNodeView() {
        return ({node}) => {
            const src: string = node.attrs.src
            let dom: HTMLElement

            if (src.endsWith('.webm')) {
                const v = document.createElement('video')
                v.src = src
                v.width = v.height = 24
                v.autoplay = true
                v.loop = true
                v.muted = true
                v.playsInline = true
                v.style.display = 'inline-block'        // ✔︎ главное
                v.style.verticalAlign = 'middle'
                v.addEventListener('ended', () => v.play().catch(() => {
                }))
                dom = v
            } else {
                const img = document.createElement('img')
                img.src = src
                img.width = img.height = 24
                img.style.display = 'inline-block'
                img.style.verticalAlign = 'middle'
                dom = img
            }

            dom.dataset.emojiId = node.attrs.id
            return {dom}
        }
    }
})

/* ── фабрика ProseMirror-plugin Suggestion («:emoji») ─────────── */
function buildSuggestion(emojis: Emoji[], editor: Editor) {
    return Suggestion<EmojiAttrs>({
        editor,
        char: ':',
        startOfLine: false,

        items: ({query}) =>
            emojis
                .filter(e => e.name.toLowerCase().startsWith(query.toLowerCase()))
                .slice(0, 10)
                .map(e => ({id: e.id, label: e.name, src: e.img_url, custom_emoji_id: e.custom_emoji_id})),

        render: () => {
            let popup: HTMLDivElement

            const paint = (items: EmojiAttrs[], cmd: (it: EmojiAttrs) => void) => {
                popup.innerHTML = ''
                for (const it of items) {
                    const row = document.createElement('div')
                    row.className =
                        'px-2 py-1 flex items-center space-x-2 cursor-pointer hover:bg-gray-100'

                    if (it.src.endsWith('.webm')) {
                        const vid = document.createElement('video')
                        vid.src = it.src
                        vid.width = vid.height = 24
                        vid.autoplay = true
                        vid.loop = true           // loop attribute alone isn’t enough everywhere
                        vid.muted = true
                        vid.playsInline = true
                        vid.addEventListener('loadeddata', () => {
                            vid
                                .play()
                                .catch(() => {/* iOS/Safari may refuse until user interaction */
                                })
                        })
                        vid.addEventListener('ended', () => {
                            vid.play().catch(() => {
                            })
                        })
                        row.appendChild(vid)
                    } else {
                        const img = document.createElement('img')
                        img.src = it.src
                        img.className = 'h-6 w-6'
                        row.appendChild(img)
                    }

                    const span = document.createElement('span')
                    span.textContent = it.label
                    row.appendChild(span)

                    row.onclick = () => cmd(it)
                    popup.appendChild(row)
                }
            }

            return {
                onStart({items, command, clientRect}) {
                    popup = document.createElement('div')
                    popup.className =
                        'absolute bg-white border rounded shadow-lg z-50 max-h-60 overflow-auto'
                    // **shrink to content**:
                    popup.style.width = 'max-content'
                    popup.style.maxWidth = '250px'

                    document.body.appendChild(popup)
                    paint(items, command)

                    // position it once
                    const box = clientRect?.()
                    if (box) {
                        popup.style.left = `${box.left}px`
                        popup.style.top = `${box.bottom + window.scrollY}px`
                    }
                },

                onUpdate({items, command}) {
                    // only repaint, keep original coords
                    paint(items, command)
                },

                onExit() {
                    popup.remove()
                },
            }
        },

        command({editor, range, props}) {
            editor
                .chain()
                .focus()
                .deleteRange(range)
                .insertContent({
                    type: 'emoji',
                    attrs: {id: props.id, name: props.label, src: props.src, custom_emoji_id: props.custom_emoji_id},
                })
                .run()
        },
    })
}


/* ── Extension-обёртка, чтобы передать editor в Suggestion ─────── */
const EmojiSuggestionExt = Extension.create<{ emojis: Emoji[] }>({
    name: 'emojiSuggestion',
    addProseMirrorPlugins() {
        return [buildSuggestion(this.options.emojis, this.editor)]
    },
})

function getPlainWithPlaceholders(doc: PMNode): string {
  return doc.textBetween(
    0,
    doc.content.size,
    undefined,      // separator for block nodes (оставляем '\n' по-умолчанию)
    '🦏',       // char for leaf / atom nodes
  )
}

export function RichEditor({emojis, initialContent = '', onChange}: Props) {
    const editor = useEditor({
        extensions: [StarterKit, EmojiNode, EmojiSuggestionExt.configure({emojis})],
        content: initialContent,

        onUpdate({editor}) {
            const text = getPlainWithPlaceholders(editor.state.doc)
            const entities: EmojiEntity[] = []

            editor.state.doc.descendants((node, pos) => {
                if (node.type.name === 'emoji') {
                    entities.push({
                        type: 'custom_emoji',
                        offset: pos - 1,
                        length: 2,
                        custom_emoji_id: node.attrs.custom_emoji_id,
                    })
                }
            })

            onChange({html: editor.getHTML(), text, entities})
        },
    })
    useEffect(() => {
    if (editor && initialContent !== undefined) {
      editor.commands.setContent(initialContent, false)
    }
  }, [editor, initialContent])
    return <EditorContent editor={editor} className="border p-2 rounded"/>
}
