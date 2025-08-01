import React from 'react'
import type {Emoji} from '../services/api'
import {nanoid} from 'nanoid'

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
export const EmojiPicker: React.FC<EmojiPickerProps> = ({
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
