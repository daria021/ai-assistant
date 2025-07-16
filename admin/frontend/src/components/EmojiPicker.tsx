import React from 'react'
import type { Emoji } from '../services/api'

interface EmojiPickerProps {
  /** Список эмодзи из БД */
  emojis: Emoji[]
  /** Вызывается при выборе одного эмодзи */
  onSelect: (emoji: Emoji) => void
}

/**
 * EmojiPicker — упрощённая модалка со всеми эмодзи.
 * Просто рендерим <video> для .webm или <img> для остального
 * с прямым src={emoji.img_url}.
 */
export const EmojiPicker: React.FC<EmojiPickerProps> = ({
  emojis,
  onSelect,
}) => {
  return (
    <div
      className="
        absolute bg-white border shadow-lg p-2
        grid grid-cols-6 gap-2
        top-full left-0 z-10
      "
    >
      {emojis.map((emoji) => {
        // Стабильный key, совпадающий с custom_emoji_id
        const key = emoji.custom_emoji_id
        const isVideo = emoji.img_url.toLowerCase().endsWith('.webm')

        return (
          <button
            key={key}
            type="button"
            onClick={() => onSelect(emoji)}
            className="p-1 hover:bg-gray-100 rounded"
          >
            {isVideo ? (
              <video
                src={emoji.img_url}
                width={24}
                height={24}
                autoPlay
                loop
                muted
                playsInline
                className="inline-block align-middle"
                onError={(e) =>
                  console.error(
                    `Emoji <video> load error for ${key}:`,
                    e
                  )
                }
              />
            ) : (
              <img
                src={emoji.img_url}
                alt={emoji.name}
                width={24}
                height={24}
                className="inline-block align-middle"
                onError={(e) =>
                  console.error(
                    `Emoji <img> load error for ${key}:`,
                    (e.target as HTMLImageElement).src
                  )
                }
              />
            )}
          </button>
        )
      })}
    </div>
  )
}
