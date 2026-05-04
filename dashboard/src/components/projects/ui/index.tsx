import type { StatusType, ChainType, Scene } from '../../../types'

export function StatusDot({ status }: { status: StatusType }) {
  const colors: Record<StatusType, string> = {
    COMPLETED: 'var(--green)',
    PROCESSING: 'var(--yellow)',
    PENDING: 'var(--muted)',
    FAILED: 'var(--red)',
  }
  return (
    <span
      className="inline-block w-2.5 h-2.5 rounded-full"
      style={{ background: colors[status], border: '2px solid var(--border)' }}
    />
  )
}

export function Badge({ label }: { label: string }) {
  return <span className="nb-badge">{label}</span>
}

export function ChainBadge({ type }: { type: ChainType }) {
  const styles: Record<ChainType, { bg: string; color: string }> = {
    ROOT: { bg: 'var(--text)', color: '#fff' },
    CONTINUATION: { bg: 'var(--green)', color: '#fff' },
    INSERT: { bg: 'var(--yellow)', color: '#000' },
  }
  const s = styles[type] ?? styles.ROOT
  return (
    <span
      className="text-[10px] font-black px-2 py-1 uppercase rounded-sm shadow-[2px_2px_0px_#000]"
      style={{ background: s.bg, color: s.color, border: 'var(--border-w) solid var(--border)' }}
    >
      {type}
    </span>
  )
}

export function SceneProgressBar({ scenes }: { scenes: Scene[] }) {
  const completed = scenes.filter(s =>
    s.vertical_image_status === 'COMPLETED' &&
    s.vertical_video_status === 'COMPLETED' &&
    s.vertical_upscale_status === 'COMPLETED'
  ).length
  const failed = scenes.filter(s =>
    s.vertical_image_status === 'FAILED' ||
    s.vertical_video_status === 'FAILED' ||
    s.vertical_upscale_status === 'FAILED'
  ).length
  const processing = scenes.filter(s =>
    s.vertical_image_status === 'PROCESSING' ||
    s.vertical_video_status === 'PROCESSING' ||
    s.vertical_upscale_status === 'PROCESSING'
  ).length

  return (
    <div className="flex items-center gap-3 text-[11px] font-bold">
      <div className="nb-progress flex-1">
        <div style={{ width: `${(completed / scenes.length) * 100}%`, background: 'var(--green)', height: '100%' }} />
      </div>
      <span style={{ color: 'var(--green)' }}>{completed} done</span>
      {processing > 0 && <span style={{ color: 'var(--yellow)' }}>{processing} gen</span>}
      {failed > 0 && <span style={{ color: 'var(--red)' }}>{failed} fail</span>}
    </div>
  )
}

export function PipelineProgressBanner({ currentStage, onCancel }: { currentStage: string | false, onCancel?: () => void }) {
  if (!currentStage) return null;
  
  const stages = [
    { match: 'Creating Video', label: 'Setup Video' },
    { match: 'Extracting Assets', label: 'Extract Entities' },
    { match: 'Generating Refs', label: 'Gen References' },
    { match: 'Writing Script', label: 'Write Script' },
    { match: 'Generating Images', label: 'Gen Images' },
    { match: 'Generating Videos', label: 'Gen Videos' },
  ];

  let activeIndex = stages.findIndex(s => currentStage.includes(s.match));
  if (activeIndex === -1) activeIndex = 0; // Default or fallback

  return (
    <div className="nb-card p-4 flex flex-col gap-3 mb-2 sticky top-4 z-50" style={{ background: '#000', color: '#fff', borderColor: 'var(--yellow)', borderWidth: '2px', boxShadow: '4px 4px 0px var(--yellow)' }}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-black uppercase tracking-wider" style={{ color: 'var(--yellow)' }}>
          🚀 FULL-THROTTLE PIPELINE ACTIVE
        </span>
        <div className="flex items-center gap-3">
          <span className="text-[12px] font-bold animate-pulse" style={{ color: 'var(--yellow)' }}>
            {currentStage}
          </span>
          {onCancel && (
            <button 
              onClick={onCancel}
              className="nb-btn text-[10px] px-2 py-1 h-auto min-h-0"
              style={{ background: 'var(--red)', color: 'white', borderColor: 'var(--red)', boxShadow: '2px 2px 0px rgba(0,0,0,0.3)' }}
            >
              STOP
            </button>
          )}
        </div>
      </div>
      
      <div className="flex items-center justify-between overflow-x-auto pb-2 gap-2 w-full">
        {stages.map((stage, idx) => {
          const isDone = idx < activeIndex;
          const isActive = idx === activeIndex;
          const isPending = idx > activeIndex;
          
          return (
            <div key={idx} className="flex items-center flex-1 gap-2 min-w-max">
              <div 
                className="flex items-center justify-center text-[10px] font-black h-7 px-3 rounded-sm transition-all shadow-sm"
                style={{ 
                  background: isDone ? 'var(--green)' : isActive ? 'var(--yellow)' : '#222',
                  color: isDone ? '#fff' : isActive ? '#000' : '#888',
                  border: '2px solid',
                  borderColor: isDone ? 'var(--green)' : isActive ? 'var(--yellow)' : '#444',
                  opacity: isPending ? 0.7 : 1,
                  transform: isActive ? 'scale(1.05)' : 'none'
                }}
              >
                {isDone ? '✓ ' : isActive ? '⚙ ' : ''}{stage.label}
              </div>
              {idx < stages.length - 1 && (
                <div className="flex-1 h-1 min-w-[20px]" style={{ background: isDone ? 'var(--green)' : '#333' }} />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
