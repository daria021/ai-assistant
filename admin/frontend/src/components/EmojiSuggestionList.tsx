import React from 'react'

interface EmojiAttrs {
    id: string
    label: string
    src: string
    custom_emoji_id: string
}

export interface EmojiSuggestionListProps {
  items: EmojiAttrs[]
  command: (it: EmojiAttrs) => void
}

export const EmojiSuggestionList: React.FC<EmojiSuggestionListProps> = ({
  items,
  command,
}) => {
  return (
    <div
      className="grid"
      style={{
        gridTemplateColumns: 'repeat(auto-fill, 32px)',
        gridAutoRows: '32px',
        gap: '4px',
        padding: '4px',
        maxHeight: '200px',
        overflowY: 'auto',
      }}
    >
      {items.map(it => (
        <div
          key={it.id}
          className="w-8 h-8 flex items-center justify-center cursor-pointer"
          onClick={() => command(it)}
        >
          {it.src.endsWith('.webm') ? (
            <video
              src={it.src}
              width={24}
              height={24}
              preload="metadata"
              autoPlay
              loop
              muted
              playsInline
            />
          ) : (
            <img src={it.src} width={24} height={24} loading="eager" />
          )}
        </div>
      ))}
    </div>
)
}
