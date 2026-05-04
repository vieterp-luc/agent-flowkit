import { useState } from 'react'
import { fetchAPI, patchAPI, postAPI } from '../../../api/client'
import type { Character } from '../../../types'
import { CreateEntityModal } from '../modals/CreateEntityModal'

export function AssetsSection({ projectId, characters, config, onRefresh }: {
  projectId: string; characters: Character[]; config: any; onRefresh: () => void
}) {
  const [createOpen, setCreateOpen] = useState(false)
  const [filter, setFilter] = useState('')
  const [selectedCharId, setSelectedCharId] = useState<string | null>(null)
  const [editDesc, setEditDesc] = useState('')
  const [editVoice, setEditVoice] = useState('')
  const [editing, setEditing] = useState(false)
  const [genRefsLoading, setGenRefsLoading] = useState(false)
  const [extractLoading, setExtractLoading] = useState(false)
  const [genRefsStatus, setGenRefsStatus] = useState<{ total: number; pending: number; processing: number; completed: number; failed: number; done: boolean } | null>(null)
  const [viewImageUrl, setViewImageUrl] = useState<string | null>(null)

  function startEdit(ch: Character) {
    setSelectedCharId(ch.id)
    setEditDesc(ch.description ?? '')
    setEditVoice(ch.voice_description ?? '')
    setEditing(true)
  }

  const scrollContainer = (elementId: string, direction: 'left' | 'right') => {
    const el = document.getElementById(elementId);
    if (el) {
      const scrollAmount = el.clientWidth * 0.8;
      el.scrollBy({ left: direction === 'right' ? scrollAmount : -scrollAmount, behavior: 'smooth' });
    }
  }

  async function saveEdit() {
    if (!selectedCharId) return
    await Promise.all([
      patchAPI(`/api/characters/${selectedCharId}`, { description: editDesc }),
      patchAPI(`/api/characters/${selectedCharId}`, { voice_description: editVoice }),
    ])
    setEditing(false)
    setSelectedCharId(null)
    onRefresh()
  }

  const [loadingChars, setLoadingChars] = useState<Record<string, boolean>>({})

  async function unlinkEntity(cid: string) {
    try {
      await fetchAPI(`/api/projects/${projectId}/characters/${cid}`, { method: 'DELETE' })
      onRefresh()
    } catch (e) { console.error(e) }
  }

  async function handleExtractAssets() {
    setExtractLoading(true)
    try {
      const payload = {
        min_characters: config.charMode === 'AUTO' ? null : config.minChars, max_characters: config.charMode === 'AUTO' ? null : config.maxChars,
        min_locations: config.locMode === 'AUTO' ? null : config.minLocs, max_locations: config.locMode === 'AUTO' ? null : config.maxLocs,
        min_visual_assets: config.otherMode === 'AUTO' ? null : config.minOthers, max_visual_assets: config.otherMode === 'AUTO' ? null : config.maxOthers
      }
      const res = await postAPI<{ success: boolean; count: number; entities: Character[] }>(`/api/projects/${projectId}/auto-extract-assets`, payload)
      onRefresh()
      
      if (res && res.entities && res.entities.length > 0) {
        setGenRefsLoading(true)
        setGenRefsStatus({ total: res.entities.length, pending: res.entities.length, processing: 0, completed: 0, failed: 0, done: false })
        
        const requests = res.entities.map(c => ({
          type: 'GENERATE_CHARACTER_IMAGE' as const,
          character_id: c.id,
          project_id: projectId,
        }))
        await postAPI('/api/requests/batch', { requests })

        const poll = async () => {
          try {
            const status = await fetchAPI<{
              total: number; pending: number; processing: number; completed: number; failed: number; done: boolean
            }>(`/api/requests/batch-status?project_id=${projectId}&type=GENERATE_CHARACTER_IMAGE`)
            setGenRefsStatus(status)
            onRefresh() // Update UI as images finish
            if (!status.done) {
              setTimeout(poll, 8000)
            } else {
              setGenRefsLoading(false)
              onRefresh()
            }
          } catch {
            setGenRefsLoading(false)
          }
        }
        setTimeout(poll, 5000)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setExtractLoading(false)
    }
  }

  async function handleGenSingleRef(e: React.MouseEvent, ch: Character) {
    e.stopPropagation()
    setLoadingChars(prev => ({ ...prev, [ch.id]: true }))
    const isRegen = !!ch.media_id
    try {
      const requests = [{
        type: isRegen ? 'REGENERATE_CHARACTER_IMAGE' : 'GENERATE_CHARACTER_IMAGE',
        character_id: ch.id,
        project_id: projectId,
      }]
      await postAPI('/api/requests/batch', { requests })
      
      const poll = async () => {
        try {
          const type = isRegen ? 'REGENERATE_CHARACTER_IMAGE' : 'GENERATE_CHARACTER_IMAGE'
          const status = await fetchAPI<{
            total: number; completed: number; failed: number; done: boolean
          }>(`/api/requests/batch-status?project_id=${projectId}&type=${type}`)
          onRefresh() // Update UI as images finish
          if (!status.done) {
            setTimeout(poll, 8000)
          } else {
            setLoadingChars(prev => ({ ...prev, [ch.id]: false }))
            onRefresh()
          }
        } catch {
          setLoadingChars(prev => ({ ...prev, [ch.id]: false }))
        }
      }
      setTimeout(poll, 5000)
    } catch (e) {
      console.error(e)
      setLoadingChars(prev => ({ ...prev, [ch.id]: false }))
    }
  }

  const hasExistingRefs = characters.filter(c => c.media_id).length > 0

  const chars = characters.filter(c => c.entity_type === 'character')
  const locs = characters.filter(c => c.entity_type === 'location')
  const others = characters.filter(c => c.entity_type !== 'character' && c.entity_type !== 'location')

  const allGroups: { label: string; items: Character[] }[] = [
    { label: 'CHARACTERS', items: chars },
    { label: 'LOCATIONS', items: locs },
    { label: 'OTHER ASSETS', items: others },
  ]

  const editingChar = characters.find(c => c.id === selectedCharId)

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="text-xl font-black uppercase tracking-wider" style={{ color: 'var(--text)' }}>
          ASSETS <span className="text-lg font-bold" style={{ color: 'var(--muted)' }}>{characters.length}</span>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={filter}
            onChange={e => setFilter(e.target.value)}
            placeholder="Filter assets..."
            className="nb-input"
          />
          <button
            onClick={handleExtractAssets}
            disabled={extractLoading || genRefsLoading}
            className="nb-btn nb-btn-primary disabled:opacity-50"
            title="Auto-extract entities from project story using AI"
          >
            {extractLoading ? 'Extracting...' : (genRefsLoading && !hasExistingRefs) ? 'Generating...' : '✨ Auto-Extract Assets'}
          </button>
          <button onClick={() => setCreateOpen(true)} className="nb-btn nb-btn-accent">
            + New Entity
          </button>
        </div>
      </div>

      {/* Batch generation progress */}
      {genRefsStatus && !genRefsStatus.done && (
        <div className="nb-card p-4 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-wider" style={{ color: 'var(--text)' }}>Generating Assets</span>
            <span className="text-[11px] font-bold" style={{ color: 'var(--muted)' }}>
              {genRefsStatus.completed}/{genRefsStatus.total}
              {genRefsStatus.failed > 0 && <span style={{ color: 'var(--red)' }}> ({genRefsStatus.failed} failed)</span>}
            </span>
          </div>
          
          <div className="flex flex-col gap-1.5">
            <div className="w-full h-3 rounded-sm flex overflow-hidden" style={{ border: 'var(--border-w) solid var(--border)' }}>
              <div className="h-full transition-all duration-300" style={{ background: 'var(--green)', width: `${(genRefsStatus.completed / Math.max(1, genRefsStatus.total)) * 100}%` }} title="Completed" />
              <div className="h-full transition-all duration-300 relative overflow-hidden" style={{ background: 'var(--yellow)', width: `${(genRefsStatus.processing / Math.max(1, genRefsStatus.total)) * 100}%` }}>
                 <div className="absolute inset-0 w-full h-full opacity-30 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.3)_25%,rgba(255,255,255,0.3)_50%,transparent_50%,transparent_75%,rgba(255,255,255,0.3)_75%,rgba(255,255,255,0.3)_100%)] bg-[length:1rem_1rem] animate-pulse" />
              </div>
              <div className="h-full transition-all duration-300" style={{ background: 'var(--red)', width: `${(genRefsStatus.failed / Math.max(1, genRefsStatus.total)) * 100}%` }} title="Failed" />
            </div>
            
            <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-wider" style={{ color: 'var(--muted)' }}>
              <div className="flex gap-4">
                <span className="flex items-center gap-1"><span className="w-2 h-2 inline-block rounded-sm" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}></span> Pending: {genRefsStatus.pending}</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 inline-block rounded-sm" style={{ background: 'var(--yellow)', border: '1px solid var(--border)' }}></span> Processing: {genRefsStatus.processing}</span>
                <span className="flex items-center gap-1"><span className="w-2 h-2 inline-block rounded-sm" style={{ background: 'var(--green)', border: '1px solid var(--border)' }}></span> Done: {genRefsStatus.completed}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Done notification */}
      {genRefsStatus?.done && (
        <div className="nb-card p-3 flex items-center justify-between" style={{ borderColor: genRefsStatus.failed > 0 ? 'var(--yellow)' : 'var(--green)' }}>
          <span className="text-[11px] font-black" style={{ color: genRefsStatus.failed > 0 ? 'var(--yellow)' : 'var(--green)' }}>
            ✓ Reference {genRefsStatus.completed > 0 ? 'generation' : 'update'} complete — {genRefsStatus.completed} done{genRefsStatus.failed > 0 ? `, ${genRefsStatus.failed} failed` : ''}
          </span>
          <button onClick={() => setGenRefsStatus(null)} className="nb-btn nb-btn-ghost" style={{ padding: '2px 8px', fontSize: 10 }}>dismiss</button>
        </div>
      )}

      {/* Entity edit drawer */}
      {editing && editingChar && (
        <div className="nb-card p-4 flex flex-col gap-3" style={{ borderColor: 'var(--text)', borderWidth: 'var(--border-w)' }}>
          <div className="flex items-center justify-between">
            <div className="text-sm font-black uppercase" style={{ color: 'var(--text)' }}>Edit: {editingChar.name}</div>
            <div className="flex gap-2">
              <button onClick={() => { setEditing(false); setSelectedCharId(null) }} className="nb-btn nb-btn-ghost">Cancel</button>
              <button onClick={saveEdit} className="nb-btn nb-btn-primary">Save</button>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="nb-label">APPEARANCE</div>
              <textarea value={editDesc} onChange={e => setEditDesc(e.target.value)} rows={3} className="nb-input resize-y" placeholder="Describe appearance..." />
            </div>
            <div>
              <div className="nb-label">VOICE DESCRIPTION</div>
              <textarea value={editVoice} onChange={e => setEditVoice(e.target.value)} rows={3} className="nb-input resize-y" placeholder="Voice description..." />
            </div>
          </div>
        </div>
      )}

      {allGroups.every(g => g.items.length === 0) ? (
        <div className="text-[11px] py-8 text-center font-bold" style={{ color: 'var(--muted)' }}>No assets yet. Create one to get started.</div>
      ) : (
        <div className="flex flex-col gap-6">
          {allGroups.filter(g => {
            if (!filter) return true
            const q = filter.toLowerCase()
            return g.items.some(c => c.name.toLowerCase().includes(q) || (c.description ?? '').toLowerCase().includes(q))
          }).map(group => (
            <div key={group.label} className="flex flex-col gap-3">
              <div className="text-[11px] font-black uppercase tracking-widest" style={{ color: 'var(--muted)' }}>
                {group.label} <span className="font-bold" style={{ fontWeight: 'normal' }}>({group.items.length})</span>
              </div>
              {group.items.length === 0 ? (
                <div className="text-[11px] font-bold" style={{ color: 'var(--muted)' }}>None</div>
              ) : (
                <div className="relative group/slider">
                  {group.items.length > 5 && (
                    <button 
                      onClick={() => scrollContainer(`slider-${group.label}`, 'left')}
                      className="absolute left-0 top-[40%] -translate-y-1/2 -ml-3 z-20 w-8 h-8 rounded-full border-2 border-black shadow-[2px_2px_0px_rgba(0,0,0,1)] flex items-center justify-center opacity-0 group-hover/slider:opacity-100 transition-all hover:scale-110"
                      style={{ background: 'var(--surface)', color: 'var(--text)' }}
                      title="Scroll Left"
                    >
                      ◀
                    </button>
                  )}
                  <div id={`slider-${group.label}`} className="flex gap-4 overflow-x-auto pb-4 snap-x relative z-10" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
                    {group.items.map(ch => (
                      <div
                        key={ch.id}
                        className="flex-shrink-0 nb-card p-2 flex flex-col gap-2 cursor-pointer relative snap-start"
                        style={{ width: 'min(200px, calc(20vw - 16px))', minWidth: '150px' }}
                        onClick={() => startEdit(ch)}
                      >
                      <button
                        onClick={e => { e.stopPropagation(); unlinkEntity(ch.id) }}
                        className="absolute top-1 right-1 w-6 h-6 flex items-center justify-center font-black text-[12px] rounded-full hover:bg-red-500 hover:text-white transition-colors"
                        style={{ background: 'var(--bg)', border: 'var(--border-w) solid var(--border)', zIndex: 10, cursor: 'pointer' }}
                        title="Unlink"
                      >✕</button>
                      <div className="overflow-hidden flex items-center justify-center rounded-md cursor-pointer group"
                        onClick={(e) => {
                          if (ch.reference_image_url) {
                            e.stopPropagation();
                            setViewImageUrl(ch.reference_image_url);
                          }
                        }}
                        style={{ width: '100%', aspectRatio: '1/1', background: 'var(--surface)', border: 'var(--border-w) solid var(--border)' }}>
                        {ch.reference_image_url ? (
                          <div className="relative w-full h-full">
                            <img 
                              src={ch.reference_image_url} 
                              alt={ch.name} 
                              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110" 
                              onError={(e) => {
                                const img = e.target as HTMLImageElement;
                                if (!img.dataset.triedLocal && ch.media_id) {
                                  img.dataset.triedLocal = 'true';
                                  img.src = `http://127.0.0.1:8100/api/flow/media-local/${ch.media_id}`;
                                  return;
                                }
                                
                                if (img.dataset.broken) return;
                                img.dataset.broken = 'true';
                                img.src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiM1NTUiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTBweCIgZmlsbD0iI2FhYSIgZHRleHQtYW5jaG9yPSJtaWRkbGUiIGFsaWdubWVudC1iYXNlbGluZT0ibWlkZGxlIj5FeHBpcmVkLiBSZWNvdmVyaW5nLi4uPC90ZXh0Pjwvc3ZnPg==';
                              }}
                            />
                            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 flex items-center justify-center transition-colors duration-300">
                              <span className="text-white opacity-0 group-hover:opacity-100 font-bold text-xs bg-black/50 px-2 py-1 rounded">View</span>
                            </div>
                          </div>
                        ) : (
                          <span className="text-[11px] font-black" style={{ color: 'var(--muted)' }}>NO REF</span>
                        )}
                      </div>
                      <div className="flex items-center justify-between gap-1 mt-1">
                        <div className="font-black text-[11px] truncate flex-1" style={{ color: 'var(--text)' }} title={ch.name}>{ch.name}</div>
                        <div className="w-2 h-2 rounded-full shrink-0 shadow-[1px_1px_0px_#000] border-[1px] border-black" style={{ background: ch.media_id ? 'var(--green)' : 'var(--red)' }} title={ch.media_id ? 'Ready' : 'Missing'} />
                      </div>
                      <button
                        onClick={e => handleGenSingleRef(e, ch)}
                        className="w-full nb-btn text-[8.5px] sm:text-[9px] xl:text-[10px] py-1.5 px-1 sm:px-2 mt-auto flex justify-center items-center shadow-sm hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:translate-y-0 transition-colors"
                        style={{ 
                          background: ch.media_id ? 'var(--yellow)' : 'var(--blue)', 
                          color: ch.media_id ? 'black' : 'white', 
                          borderRadius: '4px', 
                          border: '1px solid black' 
                        }}
                        disabled={loadingChars[ch.id]}
                      >
                        {loadingChars[ch.id] ? (
                          <span className="flex items-center justify-center gap-1 animate-pulse truncate w-full">
                            <span className="w-1.5 h-1.5 rounded-full bg-black shrink-0" />
                            <span className="truncate">Generating</span>
                          </span>
                        ) : (
                          <span className="truncate w-full">{ch.media_id ? '↻ Regenerate' : '⚡ Generate'}</span>
                        )}
                      </button>
                    </div>
                  ))}
                  </div>
                  {group.items.length > 5 && (
                    <button 
                      onClick={() => scrollContainer(`slider-${group.label}`, 'right')}
                      className="absolute right-0 top-[40%] -translate-y-1/2 -mr-3 z-20 w-8 h-8 rounded-full border-2 border-black shadow-[2px_2px_0px_rgba(0,0,0,1)] flex items-center justify-center opacity-0 group-hover/slider:opacity-100 transition-all hover:scale-110"
                      style={{ background: 'var(--surface)', color: 'var(--text)' }}
                      title="Scroll Right"
                    >
                      ▶
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Image View Modal */}
      {viewImageUrl && (
        <div 
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 sm:p-8 cursor-zoom-out"
          onClick={() => setViewImageUrl(null)}
        >
          <div className="relative max-w-full max-h-full flex items-center justify-center">
            <img 
              src={viewImageUrl} 
              alt="Reference Preview" 
              className="max-w-full max-h-[90vh] object-contain rounded-md shadow-2xl"
              style={{ border: '4px solid var(--bg)' }}
              onClick={(e) => e.stopPropagation()} 
            />
            <button 
              onClick={() => setViewImageUrl(null)}
              className="absolute -top-4 -right-4 w-10 h-10 bg-white text-black font-black text-xl rounded-full border-2 border-black flex items-center justify-center hover:bg-gray-200 shadow-[4px_4px_0px_rgba(0,0,0,1)] transition-transform hover:-translate-y-1 active:translate-y-0"
              style={{ zIndex: 101 }}
            >
              ✕
            </button>
          </div>
        </div>
      )}

      <CreateEntityModal open={createOpen} projectId={projectId} onClose={() => setCreateOpen(false)} onCreated={onRefresh} />
    </div>
  )
}
