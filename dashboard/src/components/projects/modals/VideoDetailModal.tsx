import { useState } from 'react'
import type { Video } from '../../../types'
import Modal from '../../shared/Modal'
import { Badge } from '../ui'
import { formatDate } from '../utils'
import { patchAPI, deleteAPI } from '../../../api/client'

export function VideoDetailModal({ video, onClose, onUpdated }: { video: Video; onClose: () => void; onUpdated?: () => void }) {
  const [isEditing, setIsEditing] = useState(false)
  const [title, setTitle] = useState(video.title)
  const [videoStory, setVideoStory] = useState(video.video_story || '')
  const [loading, setLoading] = useState(false)

  async function handleSave() {
    setLoading(true)
    try {
      await patchAPI(`/api/videos/${video.id}`, { title, video_story: videoStory || null })
      setIsEditing(false)
      if (onUpdated) onUpdated()
    } catch (e) {
      console.error(e)
      alert("Failed to update video")
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete() {
    if (!confirm("Are you sure you want to delete this video? This will also remove all its scenes and media.")) return;
    setLoading(true)
    try {
      await deleteAPI(`/api/videos/${video.id}`)
      if (onUpdated) onUpdated()
      onClose()
    } catch (e) {
      console.error(e)
      alert("Failed to delete video")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal open onClose={onClose} title={`VIDEO: ${video.title.toUpperCase()}`} width={600}>
      <div className="flex flex-col gap-5">
        {video.thumbnail_url && (
          <div className="overflow-hidden rounded-md flex items-center justify-center bg-black" style={{ maxHeight: 300, border: 'var(--border-w) solid var(--border)' }}>
            <img src={video.thumbnail_url} alt={video.title} className="w-full h-full object-contain" />
          </div>
        )}
        
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge label={video.status} />
            {video.orientation && (
              <span className="text-[11px] font-black uppercase px-2 py-1 bg-gray-100 rounded-sm border border-black" style={{ color: 'var(--text)' }}>
                {video.orientation}
              </span>
            )}
            {video.duration && (
              <span className="text-[11px] font-bold px-2 py-1 bg-gray-100 rounded-sm border border-black" style={{ color: 'var(--text)' }}>
                {video.duration.toFixed(1)}s
              </span>
            )}
            {video.resolution && (
              <span className="text-[11px] font-bold px-2 py-1 bg-gray-100 rounded-sm border border-black" style={{ color: 'var(--text)' }}>
                {video.resolution}
              </span>
            )}
          </div>
          <span className="text-[11px] font-bold" style={{ color: 'var(--muted)' }}>Updated {formatDate(video.updated_at)}</span>
        </div>

        {isEditing ? (
          <div className="flex flex-col gap-3">
            <div>
              <div className="nb-label">TITLE</div>
              <input type="text" value={title} onChange={e => setTitle(e.target.value)} className="nb-input w-full" />
            </div>
            <div>
              <div className="nb-label">VIDEO STORY</div>
              <textarea value={videoStory} onChange={e => setVideoStory(e.target.value)} className="nb-input w-full resize-y" rows={4} />
            </div>
            <div className="flex justify-end gap-2 mt-2">
              <button onClick={() => setIsEditing(false)} className="nb-btn nb-btn-ghost">Cancel</button>
              <button onClick={handleSave} disabled={loading} className="nb-btn nb-btn-accent">
                {loading ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        ) : (
          <>
            <div>
              <div className="flex justify-between items-end mb-1">
                <div className="nb-label m-0">TITLE</div>
                <div className="flex gap-2">
                  <button onClick={() => setIsEditing(true)} className="text-[10px] font-bold uppercase underline" style={{ color: 'var(--blue)' }}>Edit</button>
                  <button onClick={handleDelete} className="text-[10px] font-bold uppercase underline" style={{ color: 'var(--red)' }}>Delete</button>
                </div>
              </div>
              <div className="text-[14px] font-black" style={{ color: 'var(--text)' }}>
                {video.title}
              </div>
            </div>

            <div>
              <div className="nb-label">VIDEO STORY</div>
              <div className="text-[12px] p-4 font-medium leading-relaxed rounded-md" style={{ background: 'var(--surface)', border: 'var(--border-w) solid var(--border)', color: 'var(--text)', whiteSpace: 'pre-wrap' }}>
                {video.video_story || <span style={{ color: 'var(--muted)' }}>(No story provided)</span>}
              </div>
            </div>
          </>
        )}

        {video.tags && (
          <div>
            <div className="nb-label">TAGS</div>
            <div className="flex flex-wrap gap-2">
              {video.tags.split(',').map((tag: string) => {
                const t = tag.trim()
                if (!t) return null
                return <span key={t} className="nb-badge">{t}</span>
              })}
            </div>
          </div>
        )}

        {(video.vertical_url || video.horizontal_url || video.youtube_id) && (
          <div className="flex flex-col gap-3">
            <div className="nb-label">MEDIA LINKS</div>
            <div className="flex flex-wrap gap-3">
              {video.vertical_url && (
                <a href={video.vertical_url} download target="_blank" rel="noreferrer" className="nb-btn nb-btn-primary text-center flex-1" style={{ textDecoration: 'none' }}>
                  Vertical Video
                </a>
              )}
              {video.horizontal_url && (
                <a href={video.horizontal_url} download target="_blank" rel="noreferrer" className="nb-btn nb-btn-accent text-center flex-1" style={{ textDecoration: 'none' }}>
                  Horizontal Video
                </a>
              )}
              {video.youtube_id && (
                <a href={`https://youtube.com/watch?v=${video.youtube_id}`} target="_blank" rel="noreferrer" className="nb-btn text-center flex-1" style={{ background: '#FF0000', color: 'white', border: 'var(--border-w) solid var(--border)', textDecoration: 'none' }}>
                  YouTube Link
                </a>
              )}
            </div>
          </div>
        )}
      </div>
    </Modal>
  )
}
