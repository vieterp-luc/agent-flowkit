import { useState, useEffect } from 'react'
import { postAPI, deleteAPI } from '../../../api/client'
import type { Video } from '../../../types'
import { Badge } from '../ui'
import { CreateVideoModal } from '../modals/CreateVideoModal'
import { VideoDetailModal } from '../modals/VideoDetailModal'

export function VideosSection({ projectId, videos, selectedVideoId, config, onSelectVideo, onRefresh, getSceneCount, pipelineOrientation }: {
  projectId: string; videos: Video[]; selectedVideoId: string; config: any; onSelectVideo: (id: string) => void; onRefresh: () => void
  getSceneCount: (videoId: string) => number
  pipelineOrientation?: string
}) {
  const [createOpen, setCreateOpen] = useState(false)
  const [filter, setFilter] = useState('')
  const [genVideosLoading, setGenVideosLoading] = useState(false)
  const [detailModalOpen, setDetailModalOpen] = useState(false)

  async function handleDeleteVideo(e: React.MouseEvent, vid: string) {
    e.stopPropagation()
    if (!confirm("Are you sure you want to delete this video? This will also remove all its scenes and media.")) return;
    try {
      await deleteAPI(`/api/videos/${vid}`)
      onRefresh()
    } catch (err) {
      console.error(err)
      alert("Failed to delete video")
    }
  }

  async function handleAutoGenerateVideos() {
    setGenVideosLoading(true)
    try {
      await postAPI(`/api/projects/${projectId}/auto-generate-videos`, { num_videos: config.videosCount })
      onRefresh()
    } catch (e) { console.error(e) }
    finally { setGenVideosLoading(false) }
  }

  useEffect(() => {
    if (videos.length > 0 && !videos.find(v => v.id === selectedVideoId)) {
      onSelectVideo(videos[0].id)
    }
  }, [videos, selectedVideoId, onSelectVideo])

  const filtered = videos.filter(v => {
    if (!filter) return true
    const q = filter.toLowerCase()
    return v.title.toLowerCase().includes(q) || (v.video_story ?? '').toLowerCase().includes(q)
  })

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="text-xl font-black uppercase tracking-wider" style={{ color: 'var(--text)' }}>
          VIDEOS <span className="font-bold text-lg" style={{ color: 'var(--muted)' }}>{videos.length}</span>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={filter}
            onChange={e => setFilter(e.target.value)}
            placeholder="Filter videos..."
            className="nb-input"
          />
          <button onClick={handleAutoGenerateVideos} disabled={genVideosLoading} className="nb-btn nb-btn-primary" style={{ background: 'var(--yellow)', color: 'black', borderColor: 'black' }}>
            {genVideosLoading ? '✨ Generating...' : '✨ Auto-Generate Videos'}
          </button>
          <button onClick={() => setCreateOpen(true)} className="nb-btn nb-btn-accent">
            + New Video
          </button>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="text-[11px] py-4 font-bold" style={{ color: 'var(--muted)' }}>
          {videos.length === 0 ? 'No videos yet. Create one to get started.' : 'No videos match your filter.'}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map(v => {
            const isSelected = v.id === selectedVideoId
            const sceneCount = getSceneCount(v.id)
            const orientation = v.orientation || pipelineOrientation || 'HORIZONTAL'
            return (
              <div key={v.id} onClick={() => { onSelectVideo(v.id); setDetailModalOpen(true); }}
                className="nb-card p-4 flex flex-col gap-3 cursor-pointer transition-all hover:-translate-y-1 hover:shadow-[6px_6px_0px_rgba(0,0,0,1)]"
                style={{ 
                  borderColor: isSelected ? 'var(--blue)' : 'var(--border)', 
                  boxShadow: isSelected ? '6px 6px 0px rgba(41, 121, 255, 0.8)' : undefined,
                  transform: isSelected ? 'translateY(-2px)' : undefined 
                }}>
                
                <div className="w-full rounded-sm overflow-hidden flex-shrink-0 relative" style={{ border: 'var(--border-w) solid var(--border)', aspectRatio: orientation === 'HORIZONTAL' ? '16/9' : '9/16', background: 'var(--surface)' }}>
                  {v.thumbnail_url ? (
                    <img 
                      src={v.thumbnail_url} 
                      className="w-full h-full object-cover" 
                      alt="Video Thumbnail" 
                      onError={(e) => {
                        const img = e.target as HTMLImageElement;
                        const match = img.src.match(/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/i);
                        
                        if (!img.dataset.triedLocal && match && match[1]) {
                          img.dataset.triedLocal = 'true';
                          img.src = `http://127.0.0.1:8100/api/flow/media-local/${match[1]}`;
                          return;
                        }
                        
                        if (img.dataset.broken) return;
                        img.dataset.broken = 'true';
                        img.src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiM1NTUiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTBweCIgZmlsbD0iI2FhYSIgZHRleHQtYW5jaG9yPSJtaWRkbGUiIGFsaWdubWVudC1iYXNlbGluZT0ibWlkZGxlIj5FeHBpcmVkLiBSZWNvdmVyaW5nLi4uPC90ZXh0Pjwvc3ZnPg==';
                      }}
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center bg-[repeating-linear-gradient(45deg,transparent,transparent_10px,rgba(0,0,0,0.05)_10px,rgba(0,0,0,0.05)_20px)]">
                      <span className="text-[10px] font-black uppercase tracking-widest" style={{ color: 'var(--muted)' }}>
                        No Media
                      </span>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[14px] font-black" style={{ color: 'var(--text)' }}>#{v.display_order + 1} {v.title}</span>
                  <div className="ml-auto flex items-center gap-1.5">
                    <button onClick={(e) => handleDeleteVideo(e, v.id)} className="text-[10px] font-bold uppercase hover:bg-red-50 px-1.5 py-0.5 rounded transition-colors" style={{ color: 'var(--red)' }} title="Delete Video">
                      🗑
                    </button>
                    <Badge label={v.status} />
                  </div>
                </div>

                <div className="flex items-center gap-4 text-[10px] font-bold" style={{ color: 'var(--muted)' }}>
                  <span>Orientation: {orientation}</span>
                  <span>Duration: {sceneCount * 8}s</span>
                  <span>{sceneCount} scene{sceneCount !== 1 ? 's' : ''}</span>
                </div>

                {v.video_story && (
                  <div className="text-[11px] font-mono leading-relaxed line-clamp-3" style={{ color: 'var(--text)', whiteSpace: 'pre-wrap' }}>
                    {v.video_story}
                  </div>
                )}

                <div className="flex items-center gap-1 mt-auto pt-3" style={{ borderTop: '2px solid var(--border)' }}>
                  <span className="text-[10px] font-bold ml-auto" style={{ color: 'var(--muted)' }}>click for details</span>
                </div>
              </div>
            )
          })}
        </div>
      )}

      <CreateVideoModal open={createOpen} projectId={projectId} onClose={() => setCreateOpen(false)} onCreated={onRefresh} />
      {detailModalOpen && selectedVideoId && (() => {
        const video = videos.find(v => v.id === selectedVideoId);
        if (!video) return null;
        return <VideoDetailModal video={video} onClose={() => setDetailModalOpen(false)} onUpdated={onRefresh} />
      })()}
    </div>
  )
}
