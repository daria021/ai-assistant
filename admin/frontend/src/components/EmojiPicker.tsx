import React, {useEffect, useRef} from 'react'
import type {Emoji} from '../services/api'
import {nanoid} from 'nanoid'
import lottie from 'lottie-web'
import { ungzip } from 'pako'

interface LottieEmojiProps {
    src: string
    className?: string
}

/** Компонент для отображения Lottie анимаций (.tgs файлы) */
const LottieEmoji: React.FC<LottieEmojiProps> = ({ src, className = "w-8 h-8" }) => {
    const containerRef = useRef<HTMLDivElement>(null)
    const animationRef = useRef<any>(null)

    useEffect(() => {
        let aborted = false

        async function load() {
            if (!containerRef.current) return

            try {
                // .tgs — это gzip JSON. Качаем как ArrayBuffer, распаковываем, парсим
                const resp = await fetch(src, { cache: 'no-store' })
                const buf = await resp.arrayBuffer()
                const decompressed = ungzip(new Uint8Array(buf), { to: 'string' }) as unknown as string
                const json = JSON.parse(decompressed)

                if (aborted || !containerRef.current) return
                animationRef.current = lottie.loadAnimation({
                    container: containerRef.current,
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    animationData: json,
                })
            } catch (e) {
                // в случае ошибки ничего не рендерим
            }
        }

        load()

        return () => {
            aborted = true
            if (animationRef.current) {
                animationRef.current.destroy()
            }
        }
    }, [src])

    return <div ref={containerRef} className={className} />
}

interface EmojiPickerProps {
    /** Список эмодзи из БД */
    emojis: Emoji[]
    /** Вызывается при выборе одного эмодзи */
    onSelect: (emoji: Emoji) => void
}

/**
 * EmojiPicker — все эмодзи простым src,
 * с новым key={nanoid()} на каждый рендер.
 */
export const EmojiPicker: React.FC<EmojiPickerProps> = (
    {
        emojis,
        onSelect,
    }) => {
    return (
        <div
            className="
        bg-white border shadow-lg p-2
        grid grid-cols-6 gap-2
        top-full left-0 z-10
      "
        >
            {emojis.map((emoji) => {
                const isVideo = emoji.format === 'video' || emoji.img_url.toLowerCase().endsWith('.webm');
                const isLottie = emoji.format === 'lottie';

                return (
                    <button
                        key={nanoid()}                     // ← новый ключ при каждом рендере
                        type="button"
                        onClick={() => onSelect(emoji)}
                        className="p-1 hover:bg-gray-100 rounded"
                    >
                        {isVideo ? (
                            <video
                                src={emoji.img_url}
                                loop
                                muted
                                playsInline
                                className="w-8 h-8"
                                onError={e => (e.currentTarget.style.display = 'none')}
                            />
                        ) : isLottie ? (
                            <LottieEmoji
                                src={emoji.img_url}
                                className="w-8 h-8"
                            />
                        ) : (
                            <img
                                src={emoji.img_url}
                                className="w-8 h-8"
                                onError={e => (e.currentTarget.style.display = 'none')}
                            />
                        )}
                    </button>
                )
            })}
        </div>
    )
}
