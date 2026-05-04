import { useState, useEffect } from 'react'
import type { Scene } from '../../types'

interface VideoPlayerProps {
  scenes: Scene[]
  initialIndex: number
  onClose: () => void
}

function parseCharacterNames(raw: string | null): string[] {
  if (!raw) return []
  try {
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed)) return parsed
    return []
  } catch { return [] }
}

export default function VideoPlayer({ scenes, initialIndex, onClose }: VideoPlayerProps) {
  const [index, setIndex] = useState(initialIndex)
  const scene = scenes[index]

  const videoSrc = scene.vertical_upscale_url || scene.vertical_video_url || ''
  const charNames = parseCharacterNames(scene.character_names)

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowLeft' && index > 0) setIndex(i => i - 1)
      if (e.key === 'ArrowRight' && index < scenes.length - 1) setIndex(i => i + 1)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [index, scenes.length, onClose])

  function chainBadgeStyle(ct: string) {
    if (ct === 'ROOT') return { background: 'var(--text)', color: '#fff' }
    if (ct === 'CONTINUATION') return { background: 'var(--green)', color: '#fff' }
    return { background: 'var(--yellow)', color: '#000' }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(0,0,0,0.85)' }}
      onClick={onClose}
    >
      <div
        className="nb-card overflow-hidden relative"
        style={{ maxHeight: '90vh', maxWidth: '90vw' }}
        onClick={e => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          className="absolute top-3 right-3 z-10 nb-btn nb-btn-ghost w-8 h-8 p-0 flex items-center justify-center font-black"
          style={{ background: 'rgba(0,0,0,0.7)', color: '#fff', zIndex: 10 }}
          onClick={onClose}
        >
          ✕
        </button>

        {/* Video */}
        <div className="flex items-center justify-center" style={{ background: '#000', minWidth: 280, maxWidth: '60vw' }}>
          <video
            key={videoSrc}
            src={videoSrc}
            controls
            autoPlay
            className="h-full"
            style={{ maxHeight: '90vh', maxWidth: '60vw', display: 'block' }}
          />
        </div>

        {/* Sidebar */}
        <div
          className="flex flex-col p-5 gap-4 overflow-y-auto"
          style={{ width: 320, background: 'var(--bg)', borderLeft: '3px solid var(--border)' }}
        >
          <div className="flex items-center gap-2">
            <span className="nb-badge">Scene #{scene.display_order + 1}</span>
            <span className="text-[10px] font-black px-2 py-1 uppercase" style={chainBadgeStyle(scene.chain_type)}>
              {scene.chain_type}
            </span>
          </div>

          {scene.prompt && (
            <div>
              <div className="nb-label">PROMPT</div>
              <div className="text-[11px]" style={{ color: 'var(--text)' }}>{scene.prompt}</div>
            </div>
          )}

          {scene.video_prompt && (
            <div>
              <div className="nb-label">VIDEO PROMPT</div>
              <div className="text-[11px] whitespace-pre-wrap" style={{ color: 'var(--text)' }}>{scene.video_prompt}</div>
            </div>
          )}

          {charNames.length > 0 && (
            <div>
              <div className="nb-label">CHARACTERS</div>
              <div className="flex flex-wrap gap-1">
                {charNames.map(name => (
                  <span key={name} className="nb-badge">{name}</span>
                ))}
              </div>
            </div>
          )}

          {/* Download */}
          <a
            href={videoSrc}
            download={`scene-${scene.display_order + 1}.mp4`}
            className="nb-btn nb-btn-primary mt-auto text-center"
            style={{ background: 'var(--text)', color: '#fff', textDecoration: 'none' }}
          >
            Download
          </a>

          {/* Prev / Next */}
          <div className="flex gap-2">
            <button
              disabled={index === 0}
              onClick={() => setIndex(i => i - 1)}
              className="nb-btn nb-btn-ghost flex-1"
              style={{ opacity: index === 0 ? 0.3 : 1 }}
            >
              ← Prev
            </button>
            <button
              disabled={index === scenes.length - 1}
              onClick={() => setIndex(i => i + 1)}
              className="nb-btn nb-btn-ghost flex-1"
              style={{ opacity: index === scenes.length - 1 ? 0.3 : 1 }}
            >
              Next →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}