import React, {useEffect, useRef, useState} from 'react'
import type {Emoji} from '../services/api'
import { nanoid } from 'nanoid';

interface EmojiPickerProps {
    /** Список эмодзи из БД */
    emojis: Emoji[]
    /** Вызывается при выборе одного эмодзи */
    onSelect: (emoji: Emoji) => void
}

/**
 * EmojiPicker — модалка со всеми эмодзи.
 * Для каждого emoji мы:
 * 1. Однократно fetch+blob→objectURL (чтобы прокинуть куки/CORS).
 * 2. Рендерим <video> для .webm и <img> для остального,
 *    но только когда objectURL уже готов.
 * 3. Пока идёт загрузка — отображаем placeholder, чтобы не
 *    получать TypeError: Load failed из‐за src=undefined.
 */
export const EmojiPicker: React.FC<EmojiPickerProps> = ({
                                                            emojis,
                                                            onSelect,
                                                        }) => {
    // custom_emoji_id → objectURL
    const [urlMap, setUrlMap] = useState<Record<string, string>>({})
    // чтобы не перезагружать один и тот же emoji
    const loadedRef = useRef<Set<string>>(new Set())

    useEffect(() => {
        emojis.forEach(emoji => {
            const key = nanoid();
            if (key && !loadedRef.current.has(key)) {
                loadedRef.current.add(key)
                fetch(emoji.img_url, {credentials: 'include'})
                    .then(res => {
                        if (!res.ok) throw new Error(`HTTP ${res.status}`)
                        return res.blob()
                    })
                    .then(blob => {
                        const objectUrl = URL.createObjectURL(blob)
                        setUrlMap(prev => ({...prev, [key]: objectUrl}))
                    })
                    .catch(err => {
                        console.error(
                            `Failed to load emoji ${key} from ${emoji.img_url}:`,
                            err
                        )
                    })
            }
        })
    }, [emojis])

    return (
        <div
            className="
        absolute bg-white border shadow-lg p-2
        grid grid-cols-6 gap-2
        top-full left-0 z-10
      "
        >
            {emojis.map(emoji => {
                const key = emoji.custom_emoji_id
                const objectUrl = key ? urlMap[key] : undefined
                const isVideo = emoji.img_url.toLowerCase().endsWith('.webm')

                return (
                    <button
                        key={key}
                        type="button"
                        onClick={() => onSelect(emoji)}
                        className="p-1 hover:bg-gray-100 rounded"
                    >
                        {objectUrl ? (
                            isVideo ? (
                                <video
                                    src={objectUrl}
                                    width={24}
                                    height={24}
                                    autoPlay
                                    loop
                                    muted
                                    playsInline
                                    className="inline-block align-middle"
                                    onError={e =>
                                        console.error(
                                            `Emoji <video> load error for ${key}:`,
                                            e
                                        )
                                    }
                                />
                            ) : (
                                <img
                                    src={objectUrl}
                                    alt={emoji.name}
                                    width={24}
                                    height={24}
                                    className="inline-block align-middle"
                                    onError={e =>
                                        console.error(
                                            `Emoji <img> load error for ${key}:`,
                                            (e.target as HTMLImageElement).src
                                        )
                                    }
                                />
                            )
                        ) : (
                            // Плейсхолдер пока blob не загружен
                            <div
                                style={{width: 24, height: 24}}
                                className="inline-block bg-gray-200 animate-pulse"
                            />
                        )}
                    </button>
                )
            })}
        </div>
    )
}
