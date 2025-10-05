import React, { useEffect, useRef } from 'react'
import lottie from 'lottie-web'
import { ungzip } from 'pako'

interface EmojiAttrs {
    id: string
    label: string
    src: string
    custom_emoji_id: string
    format?: 'static' | 'video' | 'lottie'
}

interface LottieEmojiProps {
    src: string
    className?: string
}

/** Компонент для отображения Lottie анимаций (.tgs файлы) */
const LottieEmoji: React.FC<LottieEmojiProps> = ({ src, className = "w-6 h-6" }) => {
    const containerRef = useRef<HTMLDivElement>(null)
    const animationRef = useRef<any>(null)

    useEffect(() => {
        let aborted = false
        async function load() {
            if (!containerRef.current) return
            try {
                const resp = await fetch(src, { cache: 'no-store' })
                const buf = await resp.arrayBuffer()
                const bytes = new Uint8Array(buf)

                let jsonStr: string | null = null
                if (bytes.length >= 2 && bytes[0] === 0x1f && bytes[1] === 0x8b) {
                    try {
                        jsonStr = ungzip(bytes, { to: 'string' }) as unknown as string
                    } catch (e) {
                        console.warn('ungzip failed, try as text', e)
                    }
                }
                if (!jsonStr) {
                    try {
                        jsonStr = new TextDecoder('utf-8').decode(bytes)
                    } catch {
                        jsonStr = null
                    }
                }
                if (!jsonStr) return

                let json: any
                try {
                    json = JSON.parse(jsonStr)
                } catch (e) {
                    console.error('Invalid Lottie JSON', e)
                    return
                }

                if (aborted || !containerRef.current) return
                containerRef.current.innerHTML = ''
                animationRef.current = lottie.loadAnimation({
                    container: containerRef.current,
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    animationData: json,
                    rendererSettings: { preserveAspectRatio: 'xMidYMid meet' },
                })
            } catch (e) {
                console.error('Lottie load failed', e)
            }
        }
        load()
        return () => {
            aborted = true
            if (animationRef.current) animationRef.current.destroy()
        }
    }, [src])

    return <div ref={containerRef} className={className} />
}

interface Props {
  items: EmojiAttrs[]
  command: (it: EmojiAttrs) => void
}

export const EmojiSuggestionList: React.FC<Props> = ({ items, command }) => {
  // реф, чтобы на каждый рендер форсить reload видео
  const vidsRef = useRef<HTMLVideoElement[]>([])

  useEffect(() => {
    vidsRef.current.forEach(v => {
      v.load()
      v.play().catch(() => {})
    })
  }, [items])

  return (
    <div
      // всё через inline-стили
      style={{
        position: 'absolute',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, 32px)',
        gridAutoRows: '32px',
        gap: '4px',
        padding: '4px',
        maxHeight: '200px',
        overflowY: 'auto',
        background: 'white',
        border: '1px solid rgba(0,0,0,0.1)',
        borderRadius: '4px',
        zIndex: 10,
      }}
    >
      {items.map((it, idx) => (
        <div
          key={it.id}
          // фиксированные 32×32
          style={{
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
          }}
          // onMouseDown, чтобы не потерять фокус редактора
          onMouseDown={e => {
            e.preventDefault()
            command(it)
          }}
        >
          {(it.format === 'video' || it.src.toLowerCase().endsWith('.webm')) ? (
            <video
              // <-- bust cache
              src={`${it.src}?t=${Date.now()}`}
              width={24}
              height={24}
              preload="auto"
              autoPlay
              loop
              muted
              playsInline
              onCanPlay={e => e.currentTarget.play().catch(() => {})}
              onLoadedData={e => e.currentTarget.play().catch(() => {})}
              ref={el => {
                if (el) vidsRef.current[idx] = el
              }}
              style={{ display: 'inline-block', verticalAlign: 'middle' }}
            />
          ) : it.format === 'lottie' ? (
            <LottieEmoji
              src={`${it.src}?t=${Date.now()}`}
              className="w-6 h-6 inline-block align-middle"
            />
          ) : (
            <img
              src={`${it.src}?t=${Date.now()}`}
              width={24}
              height={24}
              loading="eager"
              style={{ display: 'inline-block', verticalAlign: 'middle' }}
              alt={it.label}
            />
          )}
        </div>
      ))}
    </div>
  )
}
