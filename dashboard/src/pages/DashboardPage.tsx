import { useState, useEffect, useCallback } from 'react'
import { fetchAPI, patchAPI } from '../api/client'
import { useWebSocket } from '../api/useWebSocket'
import type { Project, Video, Request } from '../types'
import PipelineView from '../components/pipeline/PipelineView'

interface BatchStatus {
  total: number
  pending: number
  processing: number
  completed: number
  failed: number
  done: boolean
  all_succeeded: boolean
}

const STATUS_COLORS: Record<string, string> = {
  COMPLETED: 'var(--green)',
  PROCESSING: 'var(--yellow)',
  PENDING: 'var(--muted)',
  FAILED: 'var(--red)',
}

// ---- Queue Detail Panel ----
function RequestList({ requests, onRetry }: { requests: Request[]; onRetry: (id: string) => void }) {
  if (requests.length === 0) return null

  return (
    <div className="nb-card overflow-hidden">
      <div className="text-[10px] font-black px-3 py-2 nb-label" style={{ borderBottom: '2px solid var(--border)' }}>
        QUEUE ({requests.length})
      </div>
      <div className="max-h-60 overflow-y-auto">
        {requests.slice(0, 50).map(r => (
          <div
            key={r.id}
            className="flex items-center gap-2 px-3 py-1.5 text-[11px]"
            style={{ borderBottom: '1px solid var(--muted)', opacity: 0.5 }}
          >
            <span
              className="inline-block w-2 h-2 flex-shrink-0"
              style={{ background: STATUS_COLORS[r.status] ?? 'var(--muted)', border: '1px solid var(--border)' }}
            />
            <span style={{ color: 'var(--muted)' }}>{r.type.replace(/_/g, ' ')}</span>
            <span style={{ color: 'var(--text)' }}>{r.orientation ?? ''}</span>
            {r.scene_id && <span style={{ color: 'var(--muted)' }}>scene:{String(r.scene_id).slice(0, 8)}</span>}
            {r.retry_count > 0 && (
              <span className="font-bold" style={{ color: 'var(--yellow)' }}>retry:{r.retry_count}</span>
            )}
            {r.error_message && (
              <span className="truncate flex-1 font-bold mono" style={{ color: 'var(--red)' }} title={r.error_message}>
                {r.error_message.slice(0, 60)}
              </span>
            )}
            {r.status === 'FAILED' && (
              <button
                onClick={() => onRetry(r.id)}
                className="nb-btn nb-btn-ghost flex-shrink-0"
                style={{ padding: '2px 8px', fontSize: 10 }}
              >
                Retry
              </button>
            )}
          </div>
        ))}
        {requests.length > 50 && (
          <div className="text-[11px] px-3 py-1.5 font-bold" style={{ color: 'var(--muted)' }}>
            +{requests.length - 50} more
          </div>
        )}
      </div>
    </div>
  )
}

// ---- Queue Bar ----
function QueueBar({ status, requests, onRetry }: {
  status: BatchStatus; requests: Request[]; onRetry: (id: string) => void
}) {
  const [expanded, setExpanded] = useState(false)
  const total = status.total || 1
  const pct = (n: number) => Math.round((n / total) * 100)

  return (
    <div className="flex flex-col gap-2">
      <div className="nb-card p-3 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setExpanded(e => !e)}
            className="text-[11px] font-black uppercase tracking-wider flex items-center gap-2 nb-btn nb-btn-ghost"
            style={{ padding: '4px 10px' }}
          >
            REQUEST QUEUE
            <span style={{ color: 'var(--muted)', fontSize: 10 }}>{expanded ? '▲' : '▼'}</span>
          </button>
          <div className="flex items-center gap-3 text-[11px] font-bold">
            <span style={{ color: status.processing > 0 ? 'var(--text)' : 'var(--muted)' }}>
              {status.processing > 0 ? `${status.processing} PROC` : ''}
            </span>
            <span style={{ color: 'var(--muted)' }}>{status.pending} PND</span>
            <span style={{ color: status.completed > 0 ? 'var(--green)' : 'var(--muted)' }}>
              {status.completed} OK
            </span>
            {status.failed > 0 && (
              <span className="font-black" style={{ color: 'var(--red)' }}>
                {status.failed} FAIL
              </span>
            )}
          </div>
        </div>

        {/* Progress bars */}
        <div className="flex flex-col gap-2 mt-2">
          {[
            { key: 'completed', label: 'Done', color: 'var(--green)', value: status.completed },
            { key: 'processing', label: 'Proc', color: 'var(--yellow)', value: status.processing },
            { key: 'pending', label: 'Pnd', color: 'var(--muted)', value: status.pending },
            { key: 'failed', label: 'Fail', color: 'var(--red)', value: status.failed },
          ].map(({ key, label, color, value }) => (
            <div key={key} className="flex items-center gap-2">
              <span className="text-[10px] font-black uppercase" style={{ color: 'var(--muted)', width: 36 }}>{label}</span>
              <div className="nb-progress flex-1">
                <div
                  className="nb-progress-fill"
                  style={{ width: `${pct(value)}%`, background: color }}
                />
              </div>
              <span className="text-[10px] font-black" style={{ color, width: 28, textAlign: 'right' }}>{value}</span>
            </div>
          ))}
        </div>

        {status.done && (
          <div
            className="text-[11px] font-black text-center py-1"
            style={{
              border: '2px solid',
              borderColor: status.all_succeeded ? 'var(--green)' : 'var(--yellow)',
              color: status.all_succeeded ? 'var(--green)' : 'var(--yellow)',
            }}
          >
            {status.all_succeeded ? 'ALL DONE' : 'DONE (SOME FAILED)'}
          </div>
        )}
      </div>

      {expanded && <RequestList requests={requests} onRetry={onRetry} />}
    </div>
  )
}

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [videos, setVideos] = useState<Video[]>([])
  const [selectedProject, setSelectedProject] = useState<string>('')
  const [selectedVideo, setSelectedVideo] = useState<string>('')
  const [batchStatus, setBatchStatus] = useState<BatchStatus | null>(null)
  const [requests, setRequests] = useState<Request[]>([])
  const { lastEvent } = useWebSocket()

  useEffect(() => {
    fetchAPI<{ project_id: string } | null>('/api/active-project')
      .then(active => {
        if (active?.project_id) setSelectedProject(active.project_id)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    fetchAPI<Project[]>('/api/projects')
      .then(ps => {
        setProjects(ps.filter(p => p.status !== 'DELETED'))
        if (!selectedProject && ps.length > 0) {
          fetchAPI<{ project_id: string } | null>('/api/active-project')
            .then(a => { if (!a?.project_id && ps[0]) setSelectedProject(ps[0].id) })
            .catch(() => { if (ps[0]) setSelectedProject(ps[0].id) })
        }
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (!selectedProject) { setVideos([]); setSelectedVideo(''); return }
    fetchAPI<Video[]>(`/api/videos?project_id=${selectedProject}`)
      .then(v => {
        setVideos(v)
        if (v.length > 0) {
          setSelectedVideo(prev => prev && v.some(x => x.id === prev) ? prev : v[0].id)
        } else setSelectedVideo('')
      })
      .catch(() => {})
  }, [selectedProject])

  const loadBatchStatus = useCallback(async () => {
    try {
      const [s, reqs] = await Promise.all([
        fetchAPI<BatchStatus>('/api/requests/batch-status'),
        fetchAPI<Request[]>('/api/requests'),
      ])
      setBatchStatus(s)
      setRequests(reqs)
    } catch {}
  }, [])

  useEffect(() => {
    loadBatchStatus()
    const interval = setInterval(loadBatchStatus, 5000)
    return () => clearInterval(interval)
  }, [loadBatchStatus])

  async function handleRetry(requestId: string) {
    try {
      await patchAPI(`/api/requests/${requestId}`, { status: 'PENDING', retry_count: 0 })
      loadBatchStatus()
    } catch (e) { console.error(e) }
  }

  useEffect(() => {
    if (!lastEvent) return
    if (lastEvent.type === 'project_created') {
      fetchAPI<Project[]>('/api/projects').then(ps => setProjects(ps.filter(p => p.status !== 'DELETED'))).catch(() => {})
    }
    if (lastEvent.type === 'request_completed' || lastEvent.type === 'request_failed') {
      loadBatchStatus()
    }
  }, [lastEvent, loadBatchStatus])

  const activeProjectName = projects.find(p => p.id === selectedProject)?.name

  return (
    <div className="flex flex-col gap-5 h-full">
      {/* Request Queue Bar */}
      {batchStatus && batchStatus.total > 0 && (
        <QueueBar status={batchStatus} requests={requests} onRetry={handleRetry} />
      )}

      {/* Selectors */}
      <div className="flex items-center gap-3 flex-wrap">
        <select
          value={selectedProject}
          onChange={e => { setSelectedProject(e.target.value); setSelectedVideo('') }}
          className="nb-select"
          style={{ minWidth: 180 }}
        >
          <option value="">Select project…</option>
          {projects.map(p => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>

        <select
          value={selectedVideo}
          onChange={e => setSelectedVideo(e.target.value)}
          disabled={!selectedProject || videos.length === 0}
          className="nb-select"
          style={{ minWidth: 180 }}
        >
          <option value="">Select video…</option>
          {videos.map(v => (
            <option key={v.id} value={v.id}>{v.title}</option>
          ))}
        </select>

        {activeProjectName && (
          <span className="text-[11px] font-bold" style={{ color: 'var(--muted)' }}>
            ACTIVE: <span style={{ color: 'var(--text)' }}>{activeProjectName}</span>
          </span>
        )}

        <div className="ml-auto flex items-center gap-2 text-[11px] font-bold" style={{ color: 'var(--muted)' }}>
          {selectedVideo && videos.find(v => v.id === selectedVideo) && (
            <span>{videos.find(v => v.id === selectedVideo)?.title}</span>
          )}
        </div>
      </div>

      {/* Pipeline view */}
      {selectedProject && selectedVideo ? (
        <PipelineView projectId={selectedProject} videoId={selectedVideo} />
      ) : !selectedProject ? (
        <div className="flex items-center justify-center flex-1" style={{ color: 'var(--muted)' }}>
          Select a project to view its pipeline
        </div>
      ) : videos.length === 0 ? (
        <div className="flex items-center justify-center flex-1" style={{ color: 'var(--muted)' }}>
          No videos in this project yet. Go to Projects → Detail → Videos to create one.
        </div>
      ) : (
        <div className="flex items-center justify-center flex-1" style={{ color: 'var(--muted)' }}>
          Select a video to view the pipeline
        </div>
      )}
    </div>
  )
}
