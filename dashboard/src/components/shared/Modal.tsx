import type { ReactNode } from 'react'

interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
  width?: number
}

export default function Modal({ open, onClose, title, children, width = 480 }: ModalProps) {
  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(0,0,0,0.6)' }}
      onClick={onClose}
    >
      <div
        className="nb-card overflow-hidden flex flex-col"
        style={{ width, maxWidth: '90vw', maxHeight: '90vh' }}
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-3" style={{ borderBottom: '2px solid var(--border)' }}>
          <h2 className="font-black text-sm uppercase tracking-widest" style={{ color: 'var(--text)' }}>{title}</h2>
          <button onClick={onClose} className="nb-btn nb-btn-ghost w-7 h-7 p-0" style={{ padding: 0 }}>
            ✕
          </button>
        </div>
        <div className="overflow-y-auto p-5">
          {children}
        </div>
      </div>
    </div>
  )
}