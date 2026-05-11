import { useState } from 'react'
import Modal from '../../shared/Modal'

interface SocialCaption {
  fb_caption: string
  fb_hashtags: string
  tiktok_caption: string
  tiktok_hashtags: string
}

interface Props {
  open: boolean
  onClose: () => void
  caption: SocialCaption | null
  loading: boolean
  onGenerate: () => void
}

function CopyBlock({ label, value }: { label: string; value: string }) {
  const [copied, setCopied] = useState(false)

  function copy() {
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-black uppercase tracking-wider" style={{ color: 'var(--muted)' }}>{label}</span>
        <button
          onClick={copy}
          className="nb-btn nb-btn-ghost text-[10px] px-2 py-0.5"
        >
          {copied ? '✓ Copied' : 'Copy'}
        </button>
      </div>
      <div
        className="rounded p-2 text-[12px] whitespace-pre-wrap"
        style={{ background: 'var(--surface)', border: '1.5px solid var(--border)', color: 'var(--text)', minHeight: 48 }}
      >
        {value || <span style={{ color: 'var(--muted)' }}>—</span>}
      </div>
    </div>
  )
}

export function SocialCaptionModal({ open, onClose, caption, loading, onGenerate }: Props) {
  return (
    <Modal open={open} onClose={onClose} title="📱 Caption MXH" width={520}>
      {loading ? (
        <div className="text-center py-8 text-[13px] font-bold" style={{ color: 'var(--muted)' }}>
          Đang tải...
        </div>
      ) : caption ? (
        <div className="flex flex-col gap-4">
          <div className="flex justify-end">
            <button onClick={onGenerate} disabled={loading} className="nb-btn nb-btn-ghost text-[10px] px-3 py-1">
              {loading ? '⏳' : '🔄 Tạo lại'}
            </button>
          </div>
          <div className="flex flex-col gap-3 pb-3" style={{ borderBottom: '1.5px solid var(--border)' }}>
            <div className="text-[11px] font-black uppercase tracking-widest" style={{ color: 'var(--blue)' }}>
              Facebook Reels
            </div>
            <CopyBlock label="Caption" value={caption.fb_caption} />
            <CopyBlock label="Hashtags" value={caption.fb_hashtags} />
          </div>
          <div className="flex flex-col gap-3">
            <div className="text-[11px] font-black uppercase tracking-widest" style={{ color: 'var(--text)' }}>
              TikTok
            </div>
            <CopyBlock label="Caption" value={caption.tiktok_caption} />
            <CopyBlock label="Hashtags" value={caption.tiktok_hashtags} />
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-4 py-8">
          <div className="text-[13px]" style={{ color: 'var(--muted)' }}>Chưa có caption.</div>
          <button onClick={onGenerate} disabled={loading} className="nb-btn nb-btn-primary text-[12px]">
            ✨ Tạo Caption
          </button>
        </div>
      )}
    </Modal>
  )
}
