import { useState, useEffect } from 'react'
import { fetchAPI } from '../../../api/client'
import type { Scene, StatusType } from '../../../types'
import Modal from '../../shared/Modal'
import { StatusDot, ChainBadge } from '../ui'
import { formatDate, parseCharNames } from '../utils'

export function SceneDetailModal({ scene, onClose, onRetry }: { scene: Scene; onClose: () => void; onRetry?: (sid: string) => void }) {
  const [errorExpanded, setErrorExpanded] = useState(false)
  const [failedRequests, setFailedRequests] = useState<{type: string, error_message: string}[]>([])

  useEffect(() => {
    fetchAPI<any[]>(`/api/requests?scene_id=${scene.id}&status=FAILED`)
      .then(reqs => {
        const errors = reqs.filter(r => r.error_message).map(r => ({ type: r.type, error_message: r.error_message }))
        setFailedRequests(errors)
      })
      .catch(console.error)
  }, [scene.id])

  const charNames = parseCharNames(scene.character_names)
  const thumbUrl = scene.vertical_image_url || scene.horizontal_image_url || null
  const videoUrl = scene.vertical_upscale_url || scene.vertical_video_url || scene.horizontal_video_url || null
  const orientations = [{ key: 'vertical', label: 'Vertical (9:16)' }, { key: 'horizontal', label: 'Horizontal (16:9)' }]

  return (
    <Modal open onClose={onClose} title={`SCENE #${scene.display_order + 1}`} width={560}>
      <div className="flex flex-col gap-4">
        {thumbUrl && (
          <div className="overflow-hidden rounded-md" style={{ maxHeight: 200, border: 'var(--border-w) solid var(--border)' }}>
            <img src={thumbUrl} alt={`Scene ${scene.display_order + 1}`} className="w-full h-full object-cover" />
          </div>
        )}
        <div className="flex items-center gap-2 flex-wrap">
          <ChainBadge type={scene.chain_type} />
          <StatusDot status={scene.vertical_image_status} />
          <StatusDot status={scene.vertical_video_status} />
          <StatusDot status={scene.vertical_upscale_status} />
          <span className="text-[11px] font-bold ml-auto" style={{ color: 'var(--muted)' }}>Updated {formatDate(scene.updated_at)}</span>
        </div>
        {orientations.map(({ key, label }) => {
          const imgS = scene[`${key}_image_status` as keyof Scene] as StatusType
          const vidS = scene[`${key}_video_status` as keyof Scene] as StatusType
          const upS = scene[`${key}_upscale_status` as keyof Scene] as StatusType
          return (
            <div key={key} className="nb-card p-3">
              <div className="text-[10px] font-black uppercase mb-2" style={{ color: 'var(--muted)' }}>{label}</div>
              <div className="flex items-center gap-4 text-[11px] font-bold">
                <span className="flex items-center gap-1.5"><StatusDot status={imgS} />Image</span>
                <span className="flex items-center gap-1.5"><StatusDot status={vidS} />Video</span>
                <span className="flex items-center gap-1.5"><StatusDot status={upS} />Upscale</span>
              </div>
              {key === 'vertical' && videoUrl && (
                <a href={videoUrl} download={`scene-${scene.display_order + 1}.mp4`}
                  className="nb-btn nb-btn-accent inline-block mt-3 text-center"
                  style={{ textDecoration: 'none' }}>
                  Download Video
                </a>
              )}
            </div>
          )
        })}
        <div>
          <div className="nb-label">PROMPT</div>
          <div className="text-[11px] p-3 font-mono rounded-md" style={{ background: 'var(--bg)', border: 'var(--border-w) solid var(--border)', color: 'var(--text)', whiteSpace: 'pre-wrap' }}>
            {scene.prompt || <span style={{ color: 'var(--muted)' }}>(empty)</span>}
          </div>
        </div>
        {scene.video_prompt && (
          <div>
            <div className="nb-label">VIDEO PROMPT</div>
            <div className="text-[11px] p-3 font-mono rounded-md" style={{ background: 'var(--bg)', border: 'var(--border-w) solid var(--border)', color: 'var(--text)', whiteSpace: 'pre-wrap' }}>
              {scene.video_prompt}
            </div>
          </div>
        )}
        {scene.narrator_text && (
          <div>
            <div className="nb-label">NARRATOR</div>
            <div className="text-[11px] p-3 italic rounded-md shadow-[inset_2px_2px_0px_rgba(0,0,0,0.05)]" style={{ background: 'var(--surface)', border: 'var(--border-w) solid var(--border)', color: 'var(--muted)', whiteSpace: 'pre-wrap' }}>
              "{scene.narrator_text}"
            </div>
          </div>
        )}
        {charNames.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {charNames.map(name => (
              <span key={name} className="nb-badge">{name}</span>
            ))}
          </div>
        )}
        {failedRequests.length > 0 && (
          <div className="flex flex-col gap-2">
            {failedRequests.map((req, idx) => (
              <div key={idx} className="nb-card p-3" style={{ borderColor: 'var(--red)' }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-black uppercase" style={{ color: 'var(--red)' }}>ERROR: {req.type}</span>
                  <button onClick={() => setErrorExpanded(!errorExpanded)} className="text-[11px] font-bold" style={{ color: 'var(--muted)' }}>
                    {errorExpanded ? 'collapse' : 'expand'}
                  </button>
                </div>
                <div className="text-[11px] font-mono" style={{ color: 'var(--red)', whiteSpace: 'pre-wrap' }}>
                  {errorExpanded ? req.error_message : req.error_message.slice(0, 120) + (req.error_message.length > 120 ? '...' : '')}
                </div>
                {onRetry && (
                  <button onClick={() => onRetry(scene.id)} className="nb-btn nb-btn-danger mt-3" style={{ boxShadow: '2px 2px 0px var(--red)' }}>
                    Retry Scene
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
        {(scene.trim_start != null || scene.trim_end != null) && (
          <div className="text-[11px] font-bold" style={{ color: 'var(--muted)' }}>
            Trim: {scene.trim_start ?? 0}s → {scene.trim_end ?? scene.duration ?? '?'}s
            {scene.duration && ` (${scene.duration.toFixed(1)}s)`}
          </div>
        )}
      </div>
    </Modal>
  )
}
