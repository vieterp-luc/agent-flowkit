import { useState, useEffect, useRef } from 'react'
import { fetchAPI } from '../api/client'

const BASE = 'http://127.0.0.1:8100'

interface Template {
  name: string
  audio_path: string
  text?: string
}

interface JobStatus {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  step: string | null
  progress: number
  scenes_total: number
  scenes_done: number
  output_path: string | null
  error: string | null
}

const LANGUAGES = [
  { value: 'vi', label: 'Vietnamese' },
  { value: 'en', label: 'English' },
  { value: 'zh', label: 'Chinese' },
  { value: 'ja', label: 'Japanese' },
  { value: 'ko', label: 'Korean' },
]

function stepLabel(job: JobStatus): string {
  switch (job.step) {
    case 'detecting_scenes': return 'Detecting scenes...'
    case 'generating_narrator': return 'Generating narrator text with AI...'
    case 'generating_tts': return `Generating TTS (${job.scenes_done}/${job.scenes_total})...`
    case 'concat': return 'Merging video...'
    case 'done': return 'Complete!'
    default: return job.step ?? 'Processing...'
  }
}

export default function ReupPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [videoPath, setVideoPath] = useState('')
  const [ttsTemplate, setTtsTemplate] = useState('')
  const [speed, setSpeed] = useState(1.0)
  const [language, setLanguage] = useState('vi')
  const [minScene, setMinScene] = useState(5)
  const [sfxVolume, setSfxVolume] = useState(0.25)
  const [submitting, setSubmitting] = useState(false)
  const [job, setJob] = useState<JobStatus | null>(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    fetchAPI<Record<string, Template>>('/api/tts/templates')
      .then(data => {
        const list = Array.isArray(data)
          ? data
          : Object.entries(data).map(([name, v]) => ({ ...v, name }))
        setTemplates(list)
        if (list.length > 0) setTtsTemplate(list[0].name)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (!job) return
    if (job.status === 'completed' || job.status === 'failed') {
      if (pollRef.current) clearInterval(pollRef.current)
      return
    }
    if (pollRef.current) clearInterval(pollRef.current)
    pollRef.current = setInterval(async () => {
      try {
        const updated = await fetchAPI<JobStatus>(`/api/reup/jobs/${job.job_id}`)
        setJob(updated)
        if (updated.status === 'completed' || updated.status === 'failed') {
          clearInterval(pollRef.current!)
        }
      } catch {
        clearInterval(pollRef.current!)
      }
    }, 2000)
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [job?.job_id, job?.status])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!videoPath.trim()) { setError('Video path is required'); return }
    if (!ttsTemplate) { setError('Select a TTS template'); return }

    setSubmitting(true)
    setJob(null)
    try {
      const res = await fetch(`${BASE}/api/reup/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_path: videoPath.trim(),
          tts_template: ttsTemplate,
          speed,
          language,
          min_scene_duration: minScene,
          sfx_volume: sfxVolume,
        }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      const data: JobStatus = await res.json()
      setJob(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to start job')
    } finally {
      setSubmitting(false)
    }
  }

  function handleCopy() {
    if (!job?.output_path) return
    navigator.clipboard.writeText(job.output_path).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  const isRunning = job && (job.status === 'pending' || job.status === 'processing')

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <div>
        <h2 className="text-sm font-black uppercase tracking-widest">Reup Video</h2>
        <p className="text-[11px] mt-0.5" style={{ color: 'var(--muted)' }}>
          Dub a local video with AI-generated Vietnamese narration
        </p>
      </div>

      <form onSubmit={handleSubmit} className="nb-card p-5 flex flex-col gap-4">
        {/* Video Path */}
        <div>
          <label className="text-[10px] font-bold uppercase tracking-wider block mb-1">Video Path</label>
          <input
            className="nb-input w-full text-[12px] p-2"
            placeholder="/path/to/video.mp4"
            value={videoPath}
            onChange={e => setVideoPath(e.target.value)}
            disabled={!!isRunning}
          />
        </div>

        {/* TTS Template */}
        <div>
          <label className="text-[10px] font-bold uppercase tracking-wider block mb-1">TTS Template</label>
          <select
            className="nb-input w-full text-[12px] p-2"
            value={ttsTemplate}
            onChange={e => setTtsTemplate(e.target.value)}
            disabled={!!isRunning}
          >
            {templates.length === 0 && <option value="">No templates available</option>}
            {templates.map(t => (
              <option key={t.name} value={t.name}>{t.name}</option>
            ))}
          </select>
        </div>

        {/* Speed + Language row */}
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="text-[10px] font-bold uppercase tracking-wider block mb-1">
              Speed <span style={{ color: 'var(--muted)' }}>({speed.toFixed(2)}x)</span>
            </label>
            <input
              type="range" min={0.5} max={2.0} step={0.05}
              value={speed}
              onChange={e => setSpeed(parseFloat(e.target.value))}
              className="w-full"
              disabled={!!isRunning}
            />
          </div>
          <div className="flex-1">
            <label className="text-[10px] font-bold uppercase tracking-wider block mb-1">
              SFX Volume <span style={{ color: 'var(--muted)' }}>({Math.round(sfxVolume * 100)}%)</span>
            </label>
            <input
              type="range" min={0} max={1} step={0.05}
              value={sfxVolume}
              onChange={e => setSfxVolume(parseFloat(e.target.value))}
              className="w-full"
              disabled={!!isRunning}
            />
          </div>
          <div className="flex-1">
            <label className="text-[10px] font-bold uppercase tracking-wider block mb-1">Language</label>
            <select
              className="nb-input w-full text-[12px] p-2"
              value={language}
              onChange={e => setLanguage(e.target.value)}
              disabled={!!isRunning}
            >
              {LANGUAGES.map(l => (
                <option key={l.value} value={l.value}>{l.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Min Scene Duration */}
        <div>
          <label className="text-[10px] font-bold uppercase tracking-wider block mb-1">
            Min Scene Duration (s)
          </label>
          <input
            type="number" min={2} max={30} step={1}
            className="nb-input w-full text-[12px] p-2"
            value={minScene}
            onChange={e => setMinScene(Number(e.target.value))}
            disabled={!!isRunning}
          />
        </div>

        {error && (
          <div className="text-[11px] font-bold" style={{ color: 'var(--red)' }}>{error}</div>
        )}

        <button
          type="submit"
          className="nb-btn nb-btn-primary w-full"
          disabled={submitting || !!isRunning}
        >
          {submitting ? 'Starting...' : isRunning ? 'Processing...' : 'Generate Dubbed Video'}
        </button>
      </form>

      {/* Status section */}
      {job && (
        <div className="nb-card p-5 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider">Status</span>
            <span
              className="text-[10px] font-black uppercase"
              style={{
                color: job.status === 'completed' ? 'var(--green)'
                  : job.status === 'failed' ? 'var(--red)'
                  : 'var(--text)'
              }}
            >
              {job.status}
            </span>
          </div>

          {/* Step label */}
          <div className="text-[12px]" style={{ color: 'var(--muted)' }}>
            {stepLabel(job)}
          </div>

          {/* Progress bar */}
          <div
            className="w-full h-2 overflow-hidden"
            style={{ background: 'var(--border)', border: '1.5px solid var(--border)' }}
          >
            <div
              className="h-full transition-all duration-300"
              style={{ width: `${job.progress}%`, background: 'var(--green)' }}
            />
          </div>
          <div className="text-[10px]" style={{ color: 'var(--muted)' }}>
            {job.progress}%
            {job.scenes_total > 0 && ` · Scenes: ${job.scenes_done}/${job.scenes_total}`}
          </div>

          {/* Output path */}
          {job.status === 'completed' && job.output_path && (
            <div className="flex items-center gap-2 mt-1">
              <span
                className="flex-1 text-[11px] font-mono truncate p-2"
                style={{ background: 'var(--bg)', border: '1.5px solid var(--border)' }}
                title={job.output_path}
              >
                {job.output_path}
              </span>
              <button className="nb-btn nb-btn-ghost text-[10px] px-2 py-1" onClick={handleCopy}>
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
          )}

          {/* Error */}
          {job.status === 'failed' && job.error && (
            <div className="text-[11px] font-bold p-2" style={{ color: 'var(--red)', background: 'var(--bg)', border: '1.5px solid var(--red)' }}>
              {job.error}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
