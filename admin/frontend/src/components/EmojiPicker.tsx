import React, { useState, useEffect } from 'react'
import type { Emoji } from '../services/api'

interface EmojiPickerProps {
  /** Список эмодзи из БД */
  emojis: Emoji[]
  /** Вызывается при выборе одного эмодзи */
  onSelect: (emoji: Emoji) => void
}

/**
 * EmojiPicker — простой попап со всеми эмодзи,
 * который сам загружает каждый URL через fetch+blob,
 * чтобы обойти авторизационные ограничения и CORS,
 * и рендерит WebM-файлы через <video>, а не <img>.
 */
export const EmojiPicker: React.FC<EmojiPickerProps> = ({
  emojis,
  onSelect,
}) => {
  // Словарь: custom_emoji_id → локальный objectURL
  const [urlMap, setUrlMap] = useState<Record<string, string>>({})

  useEffect(() => {
    emojis.forEach(emoji => {
      const key = emoji.custom_emoji_id
      // Если ещё не загружали этот эмодзи — выполняем запрос
      if (key && !urlMap[key]) {
        fetch(emoji.img_url, { credentials: 'include' })
          .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            return res.blob()
          })
          .then(blob => {
            const objectUrl = URL.createObjectURL(blob)
            setUrlMap(prev => ({ ...prev, [key]: objectUrl }))
          })
          .catch(err => {
            console.error(
              `Failed to load emoji ${key} from ${emoji.img_url}:`,
              err
            )
          })
      }
    })
    // Мы хотим перезапустить эффект, если список emojis изменится
  }, [emojis, urlMap])

  return (
    <div
      className="
        absolute bg-white border shadow-lg p-2
        grid grid-cols-6 gap-2
        top-full left-0 z-10
      "
    >
      {/*
        Используем emojis.map с key={emoji.custom_emoji_id}:
        - custom_emoji_id гарантированно уникален в БД,
        - стабильный ключ предотвращает потерю DOM-узлов
      */}
      {emojis.map(emoji => {
        const objectUrl = urlMap[emoji.custom_emoji_id]
        // Определяем, видео ли это по расширению URL
        const isVideo = emoji.img_url.toLowerCase().endsWith('.webm')

        return (
          <button
            key={emoji.custom_emoji_id}
            type="button"
            onClick={() => onSelect(emoji)}
            className="p-1 hover:bg-gray-100 rounded"
          >
            {isVideo ? (
              /* Для WebM используем <video>, чтобы браузер мог его воспроизвести */
              <video
                src={objectUrl}
                width={24}
                height={24}
                autoPlay
                loop
                muted
                playsInline
                className="inline-block align-middle"
              />
            ) : (
              /* Для остальных форматов — <img> */
              <img
                src={objectUrl}
                alt={emoji.name}
                width={24}
                height={24}
                className="inline-block align-middle"
                onError={e =>
                  console.error(
                    'Emoji load error src=',
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
