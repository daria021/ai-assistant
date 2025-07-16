import React, {useEffect} from 'react'
import type {Emoji} from '../services/api'

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
export const EmojiPicker: React.FC<EmojiPickerProps> = ({ emojis, onSelect }) => {
  // ensure videos reload and autoplay each time the modal opens
  useEffect(() => {
    document
      .querySelectorAll<HTMLVideoElement>('video[data-emoji-id]')
      .forEach(video => {
        video.load();
        video.play().catch(() => {});
      });
  }, []);

  return (
    <div className="grid grid-cols-8 gap-2 p-2">
      {emojis.map(emoji => {
        const isVideo = emoji.img_url.toLowerCase().endsWith('.webm');
        return (
          <button
            key={emoji.custom_emoji_id}
            type="button"
            onClick={() => onSelect(emoji)}
            className={clsx('p-1 rounded hover:bg-gray-100')}
          >
            {isVideo ? (
              <video
                data-emoji-id={emoji.custom_emoji_id}
                src={emoji.img_url}
                width={24}
                height={24}
                autoPlay
                loop
                muted
                playsInline
                preload="metadata"
                crossOrigin="anonymous"
              />
            ) : (
              <img
                src={emoji.img_url}
                alt={emoji.name}
                width={24}
                height={24}
                crossOrigin="anonymous"
              />
            )}
          </button>
        );
      })}
    </div>
  );
};