import { useState, useEffect } from 'react'
import { postAPI } from '../../../api/client'
import type { Video } from '../../../types'
import Modal from '../../shared/Modal'

export function CreateVideoModal({ open, projectId, onClose, onCreated }: { open: boolean; projectId: string; onClose: () => void; onCreated: () => void }) {
  const [title, setTitle] = useState('')
  const [videoStory, setVideoStory] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function reset() { setTitle(''); setVideoStory(''); setError('') }
  useEffect(() => { if (open) reset() }, [open])

  async function handleCreate() {
    if (!title.trim()) { setError('Title is required'); return }
    setLoading(true)
    try {
      await postAPI<Video>('/api/videos', { project_id: projectId, title: title.trim(), video_story: videoStory.trim() })
      reset()
      onCreated()
      onClose()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to create video')
    } finally { setLoading(false) }
  }

  return (
    <Modal open={open} onClose={onClose} title="NEW VIDEO">
      <div className="flex flex-col gap-3">
        <div>
          <label className="nb-label">TITLE *</label>
          <input type="text" value={title} onChange={e => setTitle(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleCreate()} placeholder="Episode 1"
            className="nb-input" autoFocus />
        </div>
        <div>
          <label className="nb-label">VIDEO STORY</label>
          <textarea value={videoStory} onChange={e => setVideoStory(e.target.value)} placeholder="Optional video story..." rows={3}
            className="nb-input resize-y" />
        </div>
        {error && <div className="text-[11px] font-bold" style={{ color: 'var(--red)' }}>{error}</div>}
        <div className="flex justify-end gap-2 mt-2">
          <button onClick={onClose} className="nb-btn nb-btn-ghost">Cancel</button>
          <button onClick={handleCreate} disabled={loading} className="nb-btn nb-btn-accent">
            {loading ? 'Creating...' : 'Create Video'}
          </button>
        </div>
      </div>
    </Modal>
  )
}
