import { useState, useEffect, useRef, useCallback } from 'react'
import { Plus, Trash2, Mic, Play, Upload, X } from 'lucide-react'
// X used in file clear button
import { fetchAPI, deleteAPI } from '../api/client'
import Modal from '../components/shared/Modal'

const BASE = 'http://127.0.0.1:8100'

interface Template {
  name: string
  audio_path: string
  text?: string
  instruct?: string
  duration?: number
}

function durationLabel(s?: number) {
  if (!s) return ''
  return `${s.toFixed(1)}s`
}

function CreateTemplateModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [name, setName] = useState('')
  const [text, setText] = useState('Năm hai nghìn không trăm hai mươi tư, thế giới thay đổi mãi mãi. Các quốc gia hưng thịnh và sụp đổ, anh hùng xuất hiện từ bóng tối, và những người bình thường đối mặt với thử thách phi thường.')
  const [instruct, setInstruct] = useState('')
  const [refFile, setRefFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!name.trim()) { setError('Template name is required'); return }
    if (!refFile && !instruct.trim()) { setError('Either upload an MP3 or enter an instruct style'); return }

    setUploading(true)
    try {
      let refAudioPath: string | null = null

      if (refFile) {
        const fd = new FormData()
        fd.append('file', refFile)
        const upRes = await fetch(`${BASE}/api/tts/upload-ref`, { method: 'POST', body: fd })
        if (!upRes.ok) throw new Error(`Upload failed: ${upRes.status}`)
        const upData = await upRes.json()
        refAudioPath = upData.path
      }

      const body: Record<string, unknown> = { name: name.trim(), text }
      if (refAudioPath) body.ref_audio = refAudioPath
      if (instruct.trim()) body.instruct = instruct.trim()

      const res = await fetch(`${BASE}/api/tts/templates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      onCreated()
      onClose()
    } catch (e: any) {
      setError(e.message || 'Failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Modal open onClose={onClose} title="New TTS Template" width={480}>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          {/* Name */}
          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider block mb-1">Template Name</label>
            <input
              className="nb-input w-full text-[12px] p-2"
              placeholder="e.g. narrator_male_vn"
              value={name}
              onChange={e => setName(e.target.value.replace(/\s+/g, '_'))}
            />
            <span className="text-[9px]" style={{ color: 'var(--muted)' }}>Alphanumeric, hyphens, underscores only</span>
          </div>

          {/* Reference Text */}
          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider block mb-1">Reference Text</label>
            <textarea
              className="nb-input w-full text-[11px] p-2 resize-none"
              rows={3}
              value={text}
              onChange={e => setText(e.target.value)}
            />
            <span className="text-[9px]" style={{ color: 'var(--muted)' }}>Text that will be spoken (used as ref_text for cloning)</span>
          </div>

          {/* Voice Source */}
          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider block mb-1">Voice Source (choose one)</label>

            {/* Upload MP3 */}
            <div
              className="nb-card p-3 flex flex-col gap-2 cursor-pointer mb-2"
              style={{ borderStyle: refFile ? 'solid' : 'dashed' }}
              onClick={() => fileRef.current?.click()}
            >
              <div className="flex items-center gap-2">
                <Upload size={13} />
                <span className="text-[11px] font-bold">Upload MP3 / WAV</span>
              </div>
              {refFile ? (
                <div className="flex items-center gap-2">
                  <span className="text-[11px]" style={{ color: 'var(--green)' }}>{refFile.name}</span>
                  <button type="button" onClick={e => { e.stopPropagation(); setRefFile(null) }}><X size={11} /></button>
                </div>
              ) : (
                <span className="text-[10px]" style={{ color: 'var(--muted)' }}>Click to browse audio file</span>
              )}
              <input
                ref={fileRef}
                type="file"
                accept="audio/*,.mp3,.wav,.m4a"
                className="hidden"
                onChange={e => { setRefFile(e.target.files?.[0] || null); e.target.value = '' }}
              />
            </div>

            {/* OR instruct */}
            <div className="flex items-center gap-2 mb-2">
              <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
              <span className="text-[10px] font-black" style={{ color: 'var(--muted)' }}>OR</span>
              <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
            </div>
            <div>
              <input
                className="nb-input w-full text-[12px] p-2"
                placeholder="e.g. male, low pitch, young adult"
                value={instruct}
                onChange={e => setInstruct(e.target.value)}
                disabled={!!refFile}
              />
              <span className="text-[9px]" style={{ color: 'var(--muted)' }}>Voice design style — ignored if MP3 uploaded</span>
            </div>
          </div>

          {error && <div className="text-[11px] font-bold" style={{ color: 'var(--red)' }}>{error}</div>}

          <button
            type="submit"
            className="nb-btn nb-btn-primary w-full mt-1"
            disabled={uploading}
          >
            {uploading ? 'Generating...' : 'Create Template'}
          </button>
        </form>
    </Modal>
  )
}

export default function TTSPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [createOpen, setCreateOpen] = useState(false)
  const [playing, setPlaying] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchAPI<Template[]>('/api/tts/templates')
      setTemplates(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function handleDelete(name: string) {
    if (!confirm(`Delete template "${name}"?`)) return
    await deleteAPI(`/api/tts/templates/${name}`)
    load()
  }

  function handlePlay(t: Template) {
    if (playing === t.name) {
      audioRef.current?.pause()
      setPlaying(null)
      return
    }
    if (audioRef.current) { audioRef.current.pause() }
    const audio = new Audio(`${BASE}/api/tts/templates/${t.name}/audio`)
    audioRef.current = audio
    audio.play().catch(() => {})
    audio.onended = () => setPlaying(null)
    setPlaying(t.name)
  }

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-black uppercase tracking-widest">TTS Templates</h2>
          <p className="text-[11px] mt-0.5" style={{ color: 'var(--muted)' }}>
            Voice templates for consistent narrator cloning across all scenes
          </p>
        </div>
        <button className="nb-btn nb-btn-primary flex items-center gap-2" onClick={() => setCreateOpen(true)}>
          <Plus size={13} /> New Template
        </button>
      </div>

      {loading ? (
        <div className="text-[11px]" style={{ color: 'var(--muted)' }}>Loading...</div>
      ) : templates.length === 0 ? (
        <div className="nb-card p-8 text-center">
          <Mic size={24} className="mx-auto mb-3" style={{ color: 'var(--muted)' }} />
          <div className="text-[12px] font-bold mb-1">No templates yet</div>
          <div className="text-[11px]" style={{ color: 'var(--muted)' }}>
            Upload an MP3 or use instruct style to create a voice template
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {templates.map(t => (
            <div key={t.name} className="nb-card p-4 flex items-center gap-4">
              <button
                className="nb-btn nb-btn-ghost flex-shrink-0"
                style={{ padding: '6px 10px' }}
                onClick={() => handlePlay(t)}
                title="Play preview"
              >
                <Play size={13} style={{ color: playing === t.name ? 'var(--blue)' : undefined }} />
              </button>

              <div className="flex-1 min-w-0">
                <div className="text-[13px] font-black truncate">{t.name}</div>
                {t.instruct && (
                  <div className="text-[10px] font-bold mt-0.5" style={{ color: 'var(--muted)' }}>
                    {t.instruct}
                  </div>
                )}
                {t.text && (
                  <div className="text-[10px] mt-1 truncate" style={{ color: 'var(--muted)' }} title={t.text}>
                    "{t.text}"
                  </div>
                )}
              </div>

              {t.duration && (
                <span className="text-[10px] font-black flex-shrink-0" style={{ color: 'var(--muted)' }}>
                  {durationLabel(t.duration)}
                </span>
              )}

              <button
                className="nb-btn nb-btn-ghost flex-shrink-0"
                style={{ padding: '6px 10px' }}
                onClick={() => handleDelete(t.name)}
                title="Delete template"
              >
                <Trash2 size={13} style={{ color: 'var(--red)' }} />
              </button>
            </div>
          ))}
        </div>
      )}

      {createOpen && (
        <CreateTemplateModal onClose={() => setCreateOpen(false)} onCreated={load} />
      )}
    </div>
  )
}
