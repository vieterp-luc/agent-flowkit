import type { LucideIcon } from 'lucide-react'

type StageStatus = 'completed' | 'processing' | 'pending' | 'failed'

interface StageNodeProps {
  name: string
  icon: LucideIcon
  completed: number
  total: number
  status: StageStatus
  isExpanded: boolean
  onClick: () => void
}

const STATUS_COLORS: Record<StageStatus, string> = {
  completed: 'var(--green)',
  processing: 'var(--yellow)',
  pending: 'var(--muted)',
  failed: 'var(--red)',
}

export default function StageNode({ name, icon: Icon, completed, total, status, isExpanded, onClick }: StageNodeProps) {
  const pct = total === 0 ? 0 : Math.round((completed / total) * 100)
  const borderColor = STATUS_COLORS[status]

  return (
    <button
      onClick={onClick}
      className="flex flex-col gap-2 p-3 text-left flex-1 min-w-0 nb-card"
      style={{
        outline: isExpanded ? `3px solid ${borderColor}` : 'none',
        outlineOffset: '2px',
        cursor: 'pointer',
      }}
    >
      <div className="flex items-center gap-2">
        <Icon size={14} />
        <span className="text-[10px] font-black uppercase tracking-widest" style={{ color: 'var(--muted)' }}>
          {name}
        </span>
        {status === 'processing' && (
          <span
            className="ml-auto inline-block w-2 h-2"
            style={{ background: 'var(--yellow)', border: '1.5px solid var(--border)' }}
          />
        )}
      </div>

      <div className="text-2xl font-black" style={{ color: 'var(--text)' }}>
        {completed}
        <span className="text-sm font-bold" style={{ color: 'var(--muted)' }}>/{total}</span>
      </div>

      <div className="nb-progress">
        <div
          className="nb-progress-fill"
          style={{ width: `${pct}%`, background: borderColor }}
        />
      </div>

      <div className="text-[10px] font-black uppercase" style={{ color: borderColor }}>
        {pct}% {status}
      </div>
    </button>
  )
}
