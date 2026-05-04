import type { Scene, StatusType } from '../../types'

type Stage = 'image' | 'video' | 'upscale'
type Orientation = 'vertical' | 'horizontal'

interface SceneCardProps {
  scene: Scene
  stage: Stage
  orientation?: Orientation
}

const STATUS_COLORS: Record<StatusType, string> = {
  COMPLETED: 'var(--green)',
  PROCESSING: 'var(--yellow)',
  PENDING: 'var(--muted)',
  FAILED: 'var(--red)',
}

const CHAIN_COLORS: Record<string, string> = {
  ROOT: 'var(--text)',
  CONTINUATION: 'var(--green)',
  INSERT: 'var(--yellow)',
}

function getStageStatus(scene: Scene, stage: Stage, orientation: Orientation): StatusType {
  const key = `${orientation}_${stage === 'upscale' ? 'upscale' : stage}_status` as keyof Scene
  const val = scene[key] as StatusType | undefined
  if (val && val !== 'PENDING') return val
  const alt = `${orientation === 'vertical' ? 'horizontal' : 'vertical'}_${stage === 'upscale' ? 'upscale' : stage}_status` as keyof Scene
  return (scene[alt] as StatusType) || 'PENDING'
}

function getThumbUrl(scene: Scene, orientation: Orientation): string | null {
  const key = `${orientation}_image_url` as keyof Scene
  return (scene[key] as string | null) || null
}

export default function SceneCard({ scene, stage, orientation = 'vertical' }: SceneCardProps) {
  const status = getStageStatus(scene, stage, orientation)
  const thumbUrl = getThumbUrl(scene, orientation)
  const prompt = (scene.prompt ?? scene.image_prompt ?? '').slice(0, 60)

  return (
    <div className="nb-card p-2 flex flex-col gap-1.5 text-[11px] cursor-pointer">
      {/* Thumbnail */}
      <div
        className="w-full overflow-hidden flex items-center justify-center"
        style={{ aspectRatio: '9/16', background: 'var(--surface)', border: '1.5px solid var(--border)' }}
      >
        {thumbUrl ? (
          <img src={thumbUrl} alt={`Scene ${scene.display_order + 1}`} className="w-full h-full object-cover" />
        ) : (
          <span style={{ color: 'var(--muted)', fontSize: 10 }}>NO IMG</span>
        )}
      </div>

      {/* Scene # + chain badge */}
      <div className="flex items-center gap-1 flex-wrap">
        <span className="font-black" style={{ color: 'var(--text)' }}>
          #{scene.display_order + 1}
        </span>
        <span
          className="px-1 font-black uppercase"
          style={{
            background: CHAIN_COLORS[scene.chain_type] ?? 'var(--muted)',
            color: scene.chain_type === 'ROOT' ? '#fff' : '#000',
            fontSize: 8,
          }}
        >
          {scene.chain_type}
        </span>
        <span
          className="ml-auto px-1 font-black uppercase"
          style={{
            background: STATUS_COLORS[status],
            color: status === 'COMPLETED' ? '#fff' : '#000',
            fontSize: 8,
          }}
        >
          {status === 'COMPLETED' ? 'OK' : status === 'PROCESSING' ? '...' : status === 'FAILED' ? 'X' : '—'}
        </span>
      </div>

      {/* Prompt */}
      {prompt && (
        <p className="truncate font-medium" style={{ color: 'var(--muted)', fontSize: 9 }} title={scene.prompt ?? ''}>
          {prompt}{(scene.prompt ?? '').length > 60 ? '…' : ''}
        </p>
      )}
    </div>
  )
}
