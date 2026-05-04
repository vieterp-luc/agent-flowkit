import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Search, Plus, Trash2, Archive, Star, MoreVertical } from 'lucide-react'
import { fetchAPI, patchAPI, postAPI, deleteAPI } from '../api/client'
import type { Project } from '../types'
import ProjectDetailPage from './ProjectDetailPage'
import Modal from '../components/shared/Modal'

type FilterTab = 'ACTIVE' | 'ARCHIVED' | 'ALL'
type SortKey = 'updated_at' | 'created_at' | 'name'

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

function TierBadge({ tier }: { tier: string | null }) {
  if (!tier) return null
  const isTwo = tier.includes('TWO')
  return (
    <span
      className="nb-badge"
      style={{
        background: isTwo ? 'var(--text)' : 'var(--surface)',
        color: isTwo ? '#fff' : 'var(--text)',
      }}
    >
      {isTwo ? 'TIER 2' : 'TIER 1'}
    </span>
  )
}

// ---- Create Project Modal ----
function CreateProjectModal({ open, onClose, onCreated }: { open: boolean; onClose: () => void; onCreated: (projectId?: string) => void }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [material, setMaterial] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function reset() { setName(''); setDescription(''); setMaterial(''); setError('') }
  useEffect(() => { if (open) reset() }, [open])

  async function handleCreate() {
    if (!name.trim()) { setError('Name is required'); return }
    setLoading(true)
    setError('')
    try {
      const p = await postAPI<Project>('/api/projects', { name: name.trim(), description: description.trim(), material })
      reset()
      onCreated(p.id)
      onClose()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to create project')
    } finally { setLoading(false) }
  }

  return (
    <Modal open={open} onClose={onClose} title="NEW PROJECT">
      <div className="flex flex-col gap-3">
        <div>
          <label className="nb-label">NAME *</label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleCreate()}
            placeholder="My awesome project"
            className="nb-input"
            autoFocus
          />
        </div>
        <div>
          <label className="nb-label">DESCRIPTION</label>
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="Optional description..."
            rows={3}
            className="nb-input resize-y"
          />
        </div>
        <div>
          <label className="nb-label">MATERIAL STYLE (OPTIONAL)</label>
          <select value={material} onChange={e => setMaterial(e.target.value)} className="nb-select w-full">
            <option value="">Not Set</option>
            <option value="3d_pixar">3D Pixar</option>
            <option value="realistic">Realistic</option>
            <option value="anime">Anime</option>
            <option value="watercolor">Watercolor</option>
            <option value="digital_art">Digital Art</option>
            <option value="fantasy">Fantasy</option>
            <option value="sci_fi">Sci-Fi</option>
          </select>
        </div>
        {error && <div className="text-[11px] font-bold" style={{ color: 'var(--red)' }}>{error}</div>}
        <div className="flex justify-end gap-2 mt-2">
          <button onClick={onClose} className="nb-btn nb-btn-ghost">Cancel</button>
          <button onClick={handleCreate} disabled={loading} className="nb-btn nb-btn-primary" style={{ background: 'var(--text)', color: '#fff' }}>
            {loading ? 'Creating...' : 'Create Project'}
          </button>
        </div>
      </div>
    </Modal>
  )
}

// ---- Delete Confirmation ----
function ConfirmDialog({ open, title, message, confirmLabel, onConfirm, onCancel, danger }: {
  open: boolean; title: string; message: string; confirmLabel: string
  onConfirm: () => void; onCancel: () => void; danger?: boolean
}) {
  return (
    <Modal open={open} onClose={onCancel} title={title} width={400}>
      <div className="flex flex-col gap-4">
        <p className="text-[11px]" style={{ color: 'var(--muted)' }}>{message}</p>
        <div className="flex justify-end gap-2">
          <button onClick={onCancel} className="nb-btn nb-btn-ghost">Cancel</button>
          <button onClick={onConfirm} className={`nb-btn ${danger ? 'nb-btn-danger' : 'nb-btn-primary'}`} style={danger ? {} : { background: 'var(--text)', color: '#fff' }}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </Modal>
  )
}

// ---- Project Card ----
function ProjectCard({ project, activeId, onClick, onDelete, onArchive, onSetActive }: {
  project: Project; activeId: string | null; onClick: () => void
  onDelete: () => void; onArchive: () => void; onSetActive: () => void
}) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="nb-card p-4 flex flex-col gap-2 relative cursor-pointer" onClick={onClick}>
      {/* Thumbnail */}
      <div className="overflow-hidden rounded-md aspect-video mb-1 flex items-center justify-center relative group" style={{ background: 'var(--surface)', border: 'var(--border-w) solid var(--border)' }}>
        {project.thumbnail_url ? (
          <img 
            src={project.thumbnail_url} 
            alt={project.name} 
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" 
            onError={(e) => {
              const img = e.target as HTMLImageElement;
              if (!img.dataset.triedLocal) {
                img.dataset.triedLocal = 'true';
                img.src = `http://127.0.0.1:8100/api/projects/${project.id}/thumbnail`;
                return;
              }
              
              // Prevent infinite loop if placeholder also fails
              if (img.dataset.broken) return;
              img.dataset.broken = 'true';
              img.src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiM1NTUiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTBweCIgZmlsbD0iI2FhYSIgZHRleHQtYW5jaG9yPSJtaWRkbGUiIGFsaWdubWVudC1iYXNlbGluZT0ibWlkZGxlIj5FeHBpcmVkLiBSZWNvdmVyaW5nLi4uPC90ZXh0Pjwvc3ZnPg==';
            }}
          />
        ) : (
          <span className="text-[10px] font-bold" style={{ color: 'var(--muted)' }}>No thumbnail</span>
        )}
      </div>

      {/* Header */}
      <div className="flex items-start gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <div className="font-black text-sm truncate" style={{ color: 'var(--text)' }} title={project.name}>
              {project.name}
            </div>
            {project.id === activeId && (
              <Star size={14} fill="var(--text)" color="var(--text)" className="flex-shrink-0" />
            )}
          </div>
          {project.description && (
            <div className="text-[11px] truncate mt-0.5" style={{ color: 'var(--muted)' }}>
              {project.description}
            </div>
          )}
        </div>

        {/* Actions menu */}
        <div className="flex items-center gap-2">
          <button
            onClick={e => { e.stopPropagation(); onDelete() }}
            className="nb-btn"
            style={{ width: 30, height: 30, padding: 0, background: 'var(--red)', color: '#fff', borderColor: 'var(--border)' }}
            title="Delete Project"
          >
            <Trash2 size={14} strokeWidth={2.5} />
          </button>
          <div className="relative">
            <button
              onClick={e => { e.stopPropagation(); setMenuOpen(!menuOpen) }}
              className="nb-btn"
              style={{ width: 30, height: 30, padding: 0, background: 'var(--text)', color: '#fff', borderColor: 'var(--border)' }}
            >
              <MoreVertical size={14} strokeWidth={2.5} />
            </button>
          {menuOpen && (
            <div
              className="absolute right-0 top-9 z-10 flex flex-col overflow-hidden"
              style={{ background: 'var(--card)', border: '2px solid var(--border)', minWidth: 140, boxShadow: 'var(--shadow)' }}
            >
              {project.id !== activeId && (
                <button
                  onClick={e => { e.stopPropagation(); setMenuOpen(false); onSetActive() }}
                  className="flex items-center gap-2 px-3 py-2 text-[11px] font-bold hover:bg-black hover:text-white text-left text-[color:var(--text)]"
                >
                  <Star size={11} /> Set Active
                </button>
              )}
              <button
                onClick={e => { e.stopPropagation(); setMenuOpen(false); onArchive() }}
                className="flex items-center gap-2 px-3 py-2 text-[11px] font-bold hover:bg-black hover:text-white text-left text-[color:var(--muted)]"
              >
                <Archive size={11} /> {project.status === 'ARCHIVED' ? 'Unarchive' : 'Archive'}
              </button>
              <button
                onClick={e => { e.stopPropagation(); setMenuOpen(false); onDelete() }}
                className="flex items-center gap-2 px-3 py-2 text-[11px] font-bold hover:bg-black hover:text-white text-left text-[color:var(--red)]"
              >
                <Trash2 size={11} /> Delete
              </button>
            </div>
          )}
        </div>
      </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap items-center gap-2 pt-2" style={{ borderTop: '2px solid var(--border)' }}>
        {project.material && (
          <span className="nb-badge">{project.material}</span>
        )}
        <TierBadge tier={project.user_paygate_tier} />
        <span className="text-[11px] ml-auto font-bold" style={{ color: 'var(--muted)' }}>
          {formatDate(project.updated_at)}
        </span>
      </div>
    </div>
  )
}

// ---- Main ProjectsPage ----
export default function ProjectsPage() {
  const { id } = useParams<{ id?: string }>()
  const navigate = useNavigate()
  const [tab, setTab] = useState<FilterTab>('ACTIVE')
  const [projects, setProjects] = useState<Project[]>([])
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState<SortKey>('updated_at')
  const [createOpen, setCreateOpen] = useState(false)
  const [confirm, setConfirm] = useState<{ action: 'delete' | 'archive' | 'unarchive'; project: Project } | null>(null)

  const loadProjects = useCallback(async () => {
    setLoading(true)
    try {
      const [all, active] = await Promise.all([
        fetchAPI<Project[]>('/api/projects'),
        fetchAPI<{ project_id: string } | null>('/api/active-project').catch(() => null),
      ])
      setProjects(all)
      setActiveProjectId(active?.project_id ?? null)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { loadProjects() }, [loadProjects])

  if (id) {
    return <ProjectDetailPage projectId={id} onBack={() => navigate('/projects')} onRefresh={loadProjects} />
  }

  async function handleAction() {
    if (!confirm) return
    const { action, project } = confirm
    setConfirm(null)
    try {
      if (action === 'delete') {
        await deleteAPI(`/api/projects/${project.id}`)
      } else {
        await patchAPI<Project>(`/api/projects/${project.id}`, { status: action === 'archive' ? 'ARCHIVED' : 'ACTIVE' })
      }
      loadProjects()
    } catch (e) { console.error(e) }
  }

  async function handleSetActive(project: Project) {
    try {
      await postAPI('/api/active-project', { project_id: project.id })
      setActiveProjectId(project.id)
    } catch (e) { console.error(e) }
  }

  const filtered = projects.filter(p => {
    if (tab === 'ALL') { if (p.status === 'DELETED') return false }
    else if (p.status !== tab) return false
    if (search) {
      const q = search.toLowerCase()
      if (!p.name.toLowerCase().includes(q) && !(p.description ?? '').toLowerCase().includes(q)) return false
    }
    return true
  }).sort((a, b) => {
    if (sort === 'name') return a.name.localeCompare(b.name)
    if (sort === 'created_at') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  })

  const tabs: FilterTab[] = ['ACTIVE', 'ARCHIVED', 'ALL']

  return (
    <div className="flex flex-col gap-5">
      {/* Toolbar */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Search */}
        <div
          className="flex items-center gap-2 px-3"
          style={{ background: 'var(--bg)', border: '2px solid var(--border)' }}
        >
          <Search size={12} color="var(--muted)" />
          <input
            type="text"
            placeholder="Search projects..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="py-2 text-[11px] outline-none bg-transparent font-semibold"
            style={{ color: 'var(--text)', minWidth: 180 }}
          />
        </div>

        {/* Sort */}
        <select
          value={sort}
          onChange={e => setSort(e.target.value as SortKey)}
          className="nb-select"
        >
          <option value="updated_at">Last Updated</option>
          <option value="created_at">Newest</option>
          <option value="name">Name A-Z</option>
        </select>

        {/* Filter tabs */}
        <div className="flex gap-1">
          {tabs.map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className="px-3 py-2 text-[11px] font-black uppercase tracking-wider"
              style={{
                background: tab === t ? 'var(--text)' : 'var(--bg)',
                color: tab === t ? '#fff' : 'var(--muted)',
                border: '2px solid var(--border)',
                cursor: 'pointer',
              }}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Create button */}
        <button
          onClick={() => setCreateOpen(true)}
          className="nb-btn nb-btn-primary ml-auto"
        >
          <Plus size={12} /> New Project
        </button>
      </div>

      {/* Stats bar */}
      {!loading && (
        <div className="text-[11px] font-bold" style={{ color: 'var(--muted)' }}>
          {filtered.length} of {projects.length} projects
          {activeProjectId && ` · Active: ${projects.find(p => p.id === activeProjectId)?.name}`}
        </div>
      )}

      {/* Grid */}
      {loading ? (
        <div className="text-[11px] font-bold" style={{ color: 'var(--muted)' }}>Loading projects...</div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 gap-3 nb-card p-8">
          <div className="text-[11px] font-bold" style={{ color: 'var(--muted)' }}>No {tab.toLowerCase()} projects{search ? ' matching search' : ''}.</div>
          <button onClick={() => setCreateOpen(true)} className="nb-btn nb-btn-primary" style={{ background: 'var(--text)', color: '#fff' }}>
            <Plus size={12} /> Create First Project
          </button>
        </div>
      ) : (
        <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
          {filtered.map(p => (
            <ProjectCard
              key={p.id}
              project={p}
              activeId={activeProjectId}
              onClick={() => navigate(`/projects/${p.id}`)}
              onDelete={() => setConfirm({ action: 'delete', project: p })}
              onArchive={() => setConfirm({ action: p.status === 'ARCHIVED' ? 'unarchive' : 'archive', project: p })}
              onSetActive={() => handleSetActive(p)}
            />
          ))}
        </div>
      )}

      <CreateProjectModal open={createOpen} onClose={() => setCreateOpen(false)} onCreated={(id) => { loadProjects(); if (id) navigate(`/projects/${id}`) }} />

      {confirm && (
        <ConfirmDialog
          open
          title={confirm.action === 'delete' ? 'DELETE PROJECT' : confirm.action === 'archive' ? 'ARCHIVE PROJECT' : 'UNARCHIVE PROJECT'}
          message={
            confirm.action === 'delete'
              ? `Delete "${confirm.project.name}"? This will set status to DELETED.`
              : `${confirm.action === 'archive' ? 'Archive' : 'Unarchive'} "${confirm.project.name}"?`
          }
          confirmLabel={confirm.action === 'delete' ? 'Delete' : confirm.action === 'archive' ? 'Archive' : 'Unarchive'}
          onConfirm={handleAction}
          onCancel={() => setConfirm(null)}
          danger={confirm.action === 'delete'}
        />
      )}
    </div>
  )
}