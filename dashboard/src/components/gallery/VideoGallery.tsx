import { useState } from 'react'
import type { Scene } from '../../types'
import VideoPlayer from './VideoPlayer'

interface VideoGalleryProps {
  scenes: Scene[]
}

export default function VideoGallery({ scenes }: VideoGalleryProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)

  const videoscenes = scenes.filter(s => s.vertical_video_url)

  if (videoscenes.length === 0) {
    return (
      <div className="flex items-center justify-center py-16 nb-card p-8" style={{ color: 'var(--muted)' }}>
        No completed videos yet.
      </div>
    )
  }

  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {videoscenes.map((scene, idx) => (
          <div
            key={scene.id}
            className="nb-card overflow-hidden cursor-pointer"
            onClick={() => setActiveIndex(idx)}
            style={{}}
          >
            {/* Thumbnail */}
            <div className="relative" style={{ aspectRatio: '9/16' }}>
              {scene.vertical_image_url ? (
                <img
                  src={scene.vertical_image_url}
                  alt={`Scene ${scene.display_order + 1}`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div
                  className="w-full h-full flex items-center justify-center"
                  style={{ background: 'var(--surface)', color: 'var(--muted)' }}
                >
                  NO IMAGE
                </div>
              )}

              {/* Overlay */}
              <div
                className="absolute inset-0 flex flex-col justify-between p-2"
                style={{ background: 'rgba(0,0,0,0.5)' }}
              >
                <div className="flex items-start justify-between">
                  <span
                    className="text-[10px] font-black px-1.5 py-0.5"
                    style={{ background: 'var(--text)', color: '#fff' }}
                  >
                    #{scene.display_order + 1}
                  </span>
                  <div className="flex gap-1">
                    {scene.vertical_video_url && (
                      <span
                        className="text-[10px] font-black px-1.5 py-0.5"
                        style={{ background: 'var(--green)', color: '#fff' }}
                      >
                        ✓
                      </span>
                    )}
                    {scene.vertical_upscale_url && (
                      <span
                        className="text-[10px] font-black px-1.5 py-0.5"
                        style={{ background: 'var(--text)', color: '#fff' }}
                      >
                        ★
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-[10px] font-semibold truncate" style={{ color: '#fff' }}>
                  {scene.prompt?.slice(0, 60) ?? ''}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {activeIndex !== null && (
        <VideoPlayer
          scenes={videoscenes}
          initialIndex={activeIndex}
          onClose={() => setActiveIndex(null)}
        />
      )}
    </>
  )
}