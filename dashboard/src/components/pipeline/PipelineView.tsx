import { useState, useEffect, useCallback } from 'react'
import { Image, Film, Zap, Users } from 'lucide-react'
import { fetchAPI } from '../../api/client'
import { useWebSocket } from '../../api/useWebSocket'
import type { Character, Scene, StatusType } from '../../types'
import StageNode from './StageNode'
import SceneCard from './SceneCard'

type ExpandedStage = 'refs' | 'image' | 'video' | 'upscale' | null
type Orientation = 'vertical' | 'horizontal'

interface PipelineViewProps {
  projectId: string
  videoId: string
}

function deriveStatus(completed: number, total: number, hasFailure: boolean) {
  if (total === 0) return 'pending' as const
  if (hasFailure) return 'failed' as const
  if (completed === total) return 'completed' as const
  if (completed > 0) return 'processing' as const
  return 'pending' as const
}

export default function PipelineView({ projectId, videoId }: PipelineViewProps) {
  const [chars, setChars] = useState<Character[]>([])
  const [scenes, setScenes] = useState<Scene[]>([])
  const [expanded, setExpanded] = useState<ExpandedStage>(null)
  const [orientation, setOrientation] = useState<Orientation>('vertical')
  const { lastEvent } = useWebSocket()

  const load = useCallback(async () => {
    const [c, s] = await Promise.all([
      fetchAPI<Character[]>(`/api/projects/${projectId}/characters`),
      fetchAPI<Scene[]>(`/api/scenes?video_id=${videoId}`),
    ])
    setChars(c)
    setScenes(s)
  }, [projectId, videoId])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    if (!lastEvent) return
    const t = lastEvent.type
    if (t === 'scene_updated' || t === 'character_updated' || t === 'request_completed' || t === 'request_failed') {
      load()
    }
  }, [lastEvent, load])

  const imgStatus = (s: Scene): StatusType =>
    s[`${orientation}_image_status` as keyof Scene] as StatusType
  const vidStatus = (s: Scene): StatusType =>
    s[`${orientation}_video_status` as keyof Scene] as StatusType
  const upsStatus = (s: Scene): StatusType =>
    s[`${orientation}_upscale_status` as keyof Scene] as StatusType

  const refsCompleted = chars.filter(c => c.media_id).length
  const refsTotal = chars.length
  const imagesCompleted = scenes.filter(s => imgStatus(s) === 'COMPLETED').length
  const imagesFailed = scenes.some(s => imgStatus(s) === 'FAILED')
  const videosCompleted = scenes.filter(s => vidStatus(s) === 'COMPLETED').length
  const videosFailed = scenes.some(s => vidStatus(s) === 'FAILED')
  const upscaleCompleted = scenes.filter(s => upsStatus(s) === 'COMPLETED').length
  const upscaleFailed = scenes.some(s => upsStatus(s) === 'FAILED')
  const total = scenes.length

  const stages = [
    { key: 'refs' as const, name: 'Refs', icon: Users, completed: refsCompleted, total: refsTotal, status: deriveStatus(refsCompleted, refsTotal, false) },
    { key: 'image' as const, name: 'Images', icon: Image, completed: imagesCompleted, total, status: deriveStatus(imagesCompleted, total, imagesFailed) },
    { key: 'video' as const, name: 'Videos', icon: Film, completed: videosCompleted, total, status: deriveStatus(videosCompleted, total, videosFailed) },
    { key: 'upscale' as const, name: 'Upscale', icon: Zap, completed: upscaleCompleted, total, status: deriveStatus(upscaleCompleted, total, upscaleFailed) },
  ]

  const toggle = (key: ExpandedStage) => setExpanded(prev => prev === key ? null : key)

  return (
    <div className="flex flex-col gap-5">
      {/* Stage nodes row */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Orientation toggle */}
        <div className="flex" style={{ border: '2px solid var(--border)' }}>
          {(['vertical', 'horizontal'] as Orientation[]).map(o => (
            <button
              key={o}
              onClick={() => setOrientation(o)}
              className="px-3 py-2 text-[11px] font-black uppercase tracking-wider"
              style={{
                background: orientation === o ? 'var(--text)' : 'var(--card)',
                color: orientation === o ? '#fff' : 'var(--muted)',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              {o === 'vertical' ? '9:16' : '16:9'}
            </button>
          ))}
        </div>

        {stages.map((stage, i) => (
          <div key={stage.key} className="flex items-center gap-3 flex-1 min-w-0">
            <StageNode
              name={stage.name}
              icon={stage.icon}
              completed={stage.completed}
              total={stage.total}
              status={stage.status}
              isExpanded={expanded === stage.key}
              onClick={() => toggle(stage.key)}
            />
            {i < stages.length - 1 && (
              <span className="flex-shrink-0 text-lg font-black" style={{ color: 'var(--border)' }}>→</span>
            )}
          </div>
        ))}
      </div>

      {/* Expanded scene grid */}
      {expanded && expanded !== 'refs' && scenes.length > 0 && (
        <div>
          <div className="text-[11px] mb-3 font-black uppercase tracking-widest" style={{ color: 'var(--muted)' }}>
            {expanded} — {scenes.length} scenes
          </div>
          <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))' }}>
            {scenes.map(scene => (
              <SceneCard key={scene.id} scene={scene} stage={expanded as 'image' | 'video' | 'upscale'} orientation={orientation} />
            ))}
          </div>
        </div>
      )}

      {/* Expanded refs grid */}
      {expanded === 'refs' && chars.length > 0 && (
        <div>
          <div className="text-[11px] mb-3 font-black uppercase tracking-widest" style={{ color: 'var(--muted)' }}>
            refs — {chars.length} entities
          </div>
          <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))' }}>
            {chars.map(c => (
              <div
                key={c.id}
                className="nb-card p-2 flex flex-col gap-2"
              >
                <div
                  className="w-full overflow-hidden flex items-center justify-center"
                  style={{ aspectRatio: '3/4', background: 'var(--surface)', border: '1.5px solid var(--border)' }}
                >
                  {c.reference_image_url ? (
                    <img src={c.reference_image_url} alt={c.name} className="w-full h-full object-cover" />
                  ) : (
                    <span style={{ color: 'var(--muted)', fontSize: 10 }}>NO REF</span>
                  )}
                </div>
                <div className="font-black text-[11px] truncate" style={{ color: 'var(--text)' }}>{c.name}</div>
                <div className="nb-label">{c.entity_type}</div>
                <div
                  className="text-[10px] font-black uppercase"
                  style={{ color: c.media_id ? 'var(--green)' : 'var(--muted)' }}
                >
                  {c.media_id ? 'READY' : 'PENDING'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
