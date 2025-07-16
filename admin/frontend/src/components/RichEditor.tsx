import {EditorContent, Extension, ReactRenderer, useEditor} from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Suggestion from '@tiptap/suggestion'
import type {Editor} from '@tiptap/core'
import {Node} from '@tiptap/core'
import type {Emoji} from '../services/api'
import type {Node as PMNode} from '@tiptap/pm/model'
import {useEffect, useRef} from "react";
import {EmojiSuggestionList} from "./EmojiSuggestionList";


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
            {
                tag: 'img[data-emoji-id]',
                getAttrs: (dom: HTMLElement) => {
                    const element = dom as HTMLElement;
                    return {
                        id: element.dataset.emojiId,
                        src: element.getAttribute('src'),
                        name: element.getAttribute('alt'),
                        custom_emoji_id: element.dataset.customEmojiId,
                    };
                },
            },
            {
                tag: 'video[data-emoji-id]',
                getAttrs: (dom: HTMLElement) => {
                    const element = dom as HTMLElement;
                    return {
                        id: element.dataset.emojiId,
                        src: element.getAttribute('src'),
                        name: '', // or some default
                        custom_emoji_id: element.dataset.customEmojiId,
                    };
                },
            },
        ]
    },


    /* — HTML-экспорт (editor.getHTML()) — */
    renderHTML({node}) {
        const src = node.attrs.src;
        const attrs = {
            'data-emoji-id': node.attrs.id,
            'data-custom-emoji-id': node.attrs.custom_emoji_id,
            src,
            width: '24',
            height: '24',
            style: 'display:inline-block;vertical-align:middle',
        };

        return src.endsWith('.webm')
            ? ['video', {...attrs, autoplay: 'true', loop: 'true', muted: 'true'}]
            : ['img', {...attrs, alt: node.attrs.name}];
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
                .filter(e => {
                        console.log("constructing emoji entity", e);
                        return e.name.toLowerCase().startsWith(query.toLowerCase());
                    }
                )
                .map(e => {
                    const mapped = {id: e.id, label: e.name, src: e.img_url, custom_emoji_id: e.custom_emoji_id};
                    console.log("mapping emoji entity", mapped);
                    return mapped;
                }),

        render: () => {
            let component: ReactRenderer

            return {
                onStart({items, command, clientRect}) {
                    component = new ReactRenderer(EmojiSuggestionList, {
                        editor,
                        props: {items, command},
                    })
                    document.body.appendChild(component.element)

                    // позиционируем корневой <div> из ReactRenderer
                    const popup = component.element as HTMLElement
                    const box = clientRect?.()
                    if (box) {
                        popup.style.left = `${box.left}px`
                        popup.style.top = `${box.bottom + window.scrollY}px`
                    }
                },
                onUpdate({items, command, clientRect}) {
                    component.updateProps({items, command})
                    const popup = component.element as HTMLElement
                    const box = clientRect?.()
                    if (box) {
                        popup.style.left = `${box.left}px`
                        popup.style.top = `${box.bottom + window.scrollY}px`
                    }
                },
                onExit() {
                    component.destroy()
                },
            }
        },

        command({editor, range, props}) {
            const attrs = {
                id: props.id,
                name: props.label,
                src: props.src,
                custom_emoji_id: props.custom_emoji_id,
            }
            editor.chain().focus().deleteRange(range).insertContent({
                type: 'emoji',
                attrs,
            }).run()
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
                    console.log("check");
                    console.log("attrs:", node.attrs);
                    console.log("check1 passed");
                    console.log("id:", node.attrs.custom_emoji_id);
                    console.log("check2 passed");
                    console.log("params check");
                    console.log(`node: ${node}; pos: ${pos}`);
                    console.log("params check passed");
                    const emojiEntry = {
                        type: 'custom_emoji',
                        offset: pos - 1,
                        length: 2,
                        custom_emoji_id: node.attrs.custom_emoji_id,
                    } as EmojiEntity;
                    // console.log("emojiEntry is ready");
                    // console.log(`emoji found ${node.attrs}, out entry ${emojiEntry}`);
                    entities.push(emojiEntry);
                }
            });

            console.log(`NEW FUCKING ENTITIES ${JSON.stringify(entities)}`);

            onChange({html: editor.getHTML(), text, entities});
        },
    })
    const prevContent = useRef(initialContent)
    useEffect(() => {
        if (editor && initialContent !== prevContent.current) {
            editor.commands.setContent(initialContent, false)
            prevContent.current = initialContent
        }
    }, [editor, initialContent]);

    return <EditorContent editor={editor} className="border p-2 rounded"/>
}
