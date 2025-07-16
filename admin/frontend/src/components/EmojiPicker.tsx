import React from 'react'
import type { Emoji } from '../services/api'

interface EmojiPickerProps {
  /** Список эмодзи из БД */
  emojis: Emoji[]
  /** Вызывается при выборе одного эмодзи */
  onSelect: (emoji: Emoji) => void
}

/**
 * Простая модалка-сетка для выбора эмодзи.
 * Важный момент: в key каждого <button> используем
 * именно emoji.custom_emoji_id — это гарантирует
 * стабильные ключи React и никаких предупреждений.
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
      {emojis.map(emoji => (
        <button
          key={emoji.custom_emoji_id}
          type="button"
          onClick={() => onSelect(emoji)}
          className="p-1 hover:bg-gray-100 rounded"
        >
          <img
            src={emoji.img_url}
            alt={emoji.name}
            width={24}
            height={24}
            className="inline-block align-middle"
          />
        </button>
      ))}
    </div>
  )
}
