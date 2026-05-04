import { useState, useEffect, useCallback, useRef } from 'react'
import { Plus, Trash2, Edit2, LibraryBig, Palette, FileText, X } from 'lucide-react'
import { fetchAPI, postAPI, deleteAPI, patchAPI } from '../api/client'
import Modal from '../components/shared/Modal'
import type { Skill, Material } from '../types'

type Tab = 'SKILLS' | 'MATERIALS'

export default function LibraryPage() {
  const [tab, setTab] = useState<Tab>('SKILLS')
  const [skills, setSkills] = useState<Skill[]>([])
  const [materials, setMaterials] = useState<Material[]>([])
  const [loading, setLoading] = useState(true)

  // Skill Modals State
  const [skillModalOpen, setSkillModalOpen] = useState(false)
  const [editingSkill, setEditingSkill] = useState<Skill | null>(null)
  
  // Material Modals State
  const [materialModalOpen, setMaterialModalOpen] = useState(false)
  const [editingMaterial, setEditingMaterial] = useState<Material | null>(null)

  // Upload State
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isUploading, setIsUploading] = useState(false)

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [fetchedSkills, fetchedMaterials] = await Promise.all([
        fetchAPI<Skill[]>('/api/library-skills'),
        fetchAPI<Material[]>('/api/materials')
      ])
      setSkills(fetchedSkills)
      setMaterials(fetchedMaterials)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  async function handleDeleteSkill(id: string) {
    if (!confirm('Are you sure you want to delete this skill?')) return
    try {
      await deleteAPI(`/api/library-skills/${id}`)
      loadData()
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to delete')
    }
  }

  async function handleDeleteMaterial(id: string) {
    if (!confirm('Are you sure you want to delete this material?')) return
    try {
      await deleteAPI(`/api/materials/${id}`)
      loadData()
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to delete')
    }
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const res = await fetch('/api/materials/extract-and-create', {
        method: 'POST',
        body: formData
      })
      if (!res.ok) throw new Error(await res.text())
      
      await loadData()
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (err) {
      console.error(err)
      alert("Failed to extract material style from image.")
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="flex flex-col gap-5 h-full">
      {/* Header & Tabs */}
      <div className="flex items-center gap-4">
        <div className="flex gap-2 p-1" style={{ background: 'var(--surface)', border: '2px solid var(--border)' }}>
          <button
            onClick={() => setTab('SKILLS')}
            className={`flex items-center gap-2 px-4 py-2 text-xs font-bold uppercase ${tab === 'SKILLS' ? 'bg-black text-white' : 'text-gray-500'}`}
          >
            <LibraryBig size={14} /> Agent Skills
          </button>
          <button
            onClick={() => setTab('MATERIALS')}
            className={`flex items-center gap-2 px-4 py-2 text-xs font-bold uppercase ${tab === 'MATERIALS' ? 'bg-black text-white' : 'text-gray-500'}`}
          >
            <Palette size={14} /> Material Styles
          </button>
        </div>
        
        {tab === 'SKILLS' ? (
          <button onClick={() => { setEditingSkill(null); setSkillModalOpen(true); }} className="nb-btn nb-btn-primary ml-auto">
            <Plus size={14} /> Add Skill
          </button>
        ) : (
          <button onClick={() => !isUploading && fileInputRef.current?.click()} className="nb-btn nb-btn-primary ml-auto">
            <Plus size={14} /> {isUploading ? 'Extracting...' : 'AI Extract Material'}
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-sm font-bold text-gray-500 p-8">Loading library...</div>
      ) : (
        <div className="flex-1 overflow-auto">
          {tab === 'SKILLS' && (
            <div className="flex flex-col gap-6">
              {skills.length === 0 ? (
                <div className="text-sm text-gray-400 p-4">No skills found.</div>
              ) : (
                Object.entries(
                  skills.reduce((acc, skill) => {
                    const g = skill.group || 'GENERAL'
                    if (!acc[g]) acc[g] = []
                    acc[g].push(skill)
                    return acc
                  }, {} as Record<string, Skill[]>)
                ).sort(([a], [b]) => a.localeCompare(b)).map(([group, groupSkills]) => (
                  <div key={group} className="flex flex-col gap-3">
                    <h3 className="font-black text-sm uppercase text-gray-500 border-b-2 border-gray-200 pb-1">{group}</h3>
                    <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))' }}>
                      {groupSkills.map(s => (
                        <div key={s.id} className="nb-card p-4 flex flex-col gap-3">
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-2 font-black text-sm">
                              <FileText size={16} /> {s.name}
                            </div>
                            <div className="flex items-center gap-1">
                              <button onClick={() => { setEditingSkill(s); setSkillModalOpen(true); }} className="nb-btn nb-btn-ghost p-1">
                                <Edit2 size={12} />
                              </button>
                              <button onClick={() => handleDeleteSkill(s.id)} className="nb-btn nb-btn-ghost p-1 text-red-500 hover:text-red-700">
                                <Trash2 size={12} />
                              </button>
                            </div>
                          </div>
                          <div className="text-xs text-gray-600 line-clamp-3">
                            {s.description || 'No description provided.'}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {tab === 'MATERIALS' && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 pb-4">
              <div onClick={() => !isUploading && fileInputRef.current?.click()} className="nb-card flex flex-col overflow-hidden group cursor-pointer hover:-translate-y-1 transition-transform relative">
                <div className="aspect-square w-full border-b flex flex-col items-center justify-center bg-[var(--surface)]" style={{ borderColor: 'var(--border)' }}>
                  {isUploading ? (
                    <span className="animate-pulse text-sm font-black uppercase text-[var(--blue)]">Extracting AI Style...</span>
                  ) : (
                    <>
                      <span className="text-4xl font-light" style={{ color: 'var(--muted)' }}>+</span>
                      <span className="text-sm font-bold uppercase mt-2" style={{ color: 'var(--text)' }}>AI Extract from Image</span>
                    </>
                  )}
                </div>
                <div className="p-4 flex flex-col gap-3 justify-center bg-[var(--surface)] h-full">
                  <div className="text-xs text-gray-500 text-center">
                    Upload a reference image to automatically extract its visual style and lighting setup into a new material.
                  </div>
                </div>
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileChange} 
                  accept="image/*" 
                  className="hidden" 
                />
              </div>

              {materials.map(m => (
                <div key={m.id} className="nb-card flex flex-col overflow-hidden group">
                  <div className="aspect-square w-full border-b relative overflow-hidden" style={{ borderColor: 'var(--border)' }}>
                    <img 
                      src={`/materials/${m.id}_preview.png`} 
                      alt={m.name} 
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" 
                      onError={(e) => { (e.target as HTMLImageElement).src = 'https://placehold.co/400x400/222/555?text=Preview' }} 
                    />
                    <div className="absolute top-2 right-2 z-10">
                      {m.is_builtin ? (
                        <span className="text-[10px] font-black uppercase px-2 py-1 rounded-sm shadow-[2px_2px_0px_#000]" style={{ background: 'var(--text)', color: 'var(--bg)', border: 'var(--border-w) solid var(--border)' }}>
                          BUILT-IN
                        </span>
                      ) : (
                        <span className="text-[10px] font-black uppercase px-2 py-1 rounded-sm shadow-[2px_2px_0px_#000]" style={{ background: 'var(--yellow)', color: 'black', border: 'var(--border-w) solid var(--border)' }}>
                          USER
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="p-4 flex flex-col gap-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="font-black text-sm flex items-center gap-2">
                          {m.name} 
                        </div>
                        <div className="text-[10px] text-gray-400 font-mono mt-1">{m.id}</div>
                      </div>
                      {!m.is_builtin && (
                        <div className="flex items-center gap-1">
                          <button onClick={() => { setEditingMaterial(m); setMaterialModalOpen(true); }} className="nb-btn nb-btn-ghost p-1">
                            <Edit2 size={12} />
                          </button>
                          <button onClick={() => handleDeleteMaterial(m.id)} className="nb-btn nb-btn-ghost p-1 text-red-500 hover:text-red-700">
                            <Trash2 size={12} />
                          </button>
                        </div>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 line-clamp-3" title={m.style_instruction}>
                      <span className="font-bold">Prompt:</span> {m.style_instruction}
                    </div>
                  </div>
                </div>
              ))}
              {materials.length === 0 && <div className="text-sm text-gray-400 p-4">No materials found.</div>}
            </div>
          )}
        </div>
      )}

      {/* Skill Modal */}
      {skillModalOpen && (
        <SkillEditor 
          skill={editingSkill} 
          onClose={() => setSkillModalOpen(false)} 
          onSave={loadData} 
        />
      )}

      {/* Material Modal */}
      {materialModalOpen && (
        <MaterialEditor 
          material={editingMaterial} 
          onClose={() => setMaterialModalOpen(false)} 
          onSave={loadData} 
        />
      )}
    </div>
  )
}

function SkillEditor({ skill, onClose, onSave }: { skill: Skill | null, onClose: () => void, onSave: () => void }) {
  const [id, setId] = useState(skill?.id || '')
  const [content, setContent] = useState(skill?.content || '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSave() {
    if (!id.trim()) { setError('ID is required'); return }
    setLoading(true)
    setError('')
    try {
      if (skill) {
        await patchAPI(`/api/library-skills/${skill.id}`, { content })
      } else {
        await postAPI(`/api/library-skills`, { id: id.trim(), content })
      }
      onSave()
      onClose()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal open onClose={onClose} title={skill ? "EDIT SKILL" : "NEW SKILL"} width={800}>
      <div className="flex flex-col gap-4">
        <div>
          <label className="nb-label">SKILL ID (FILENAME WITHOUT .MD)</label>
          <input 
            className="nb-input" 
            value={id} 
            onChange={e => setId(e.target.value)} 
            disabled={!!skill}
            placeholder="e.g. my-custom-skill"
          />
        </div>
        <div className="flex-1 flex flex-col">
          <label className="nb-label">MARKDOWN CONTENT</label>
          <textarea 
            className="nb-input flex-1 font-mono text-sm" 
            rows={15}
            value={content} 
            onChange={e => setContent(e.target.value)} 
            placeholder="# Skill Details..."
          />
        </div>
        {error && <div className="text-red-500 text-xs font-bold">{error}</div>}
        <div className="flex justify-end gap-2">
          <button onClick={onClose} className="nb-btn nb-btn-ghost">Cancel</button>
          <button onClick={handleSave} disabled={loading} className="nb-btn nb-btn-primary bg-black text-white">
            {loading ? 'Saving...' : 'Save Skill'}
          </button>
        </div>
      </div>
    </Modal>
  )
}

function MaterialEditor({ material, onClose, onSave }: { material: Material | null, onClose: () => void, onSave: () => void }) {
  const [id, setId] = useState(material?.id || '')
  const [name, setName] = useState(material?.name || '')
  const [styleInstruction, setStyleInstruction] = useState(material?.style_instruction || '')
  const [negativePrompt, setNegativePrompt] = useState(material?.negative_prompt || '')
  const [scenePrefix, setScenePrefix] = useState(material?.scene_prefix || '')
  const [lighting, setLighting] = useState(material?.lighting || '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSave() {
    if (!id.trim() || !name.trim() || !styleInstruction.trim()) { setError('ID, Name, and Style Instruction are required'); return }
    setLoading(true)
    setError('')
    try {
      const payload = {
        name,
        style_instruction: styleInstruction,
        negative_prompt: negativePrompt,
        scene_prefix: scenePrefix,
        lighting
      }
      if (material) {
        await patchAPI(`/api/materials/${material.id}`, payload)
      } else {
        await postAPI(`/api/materials`, { id: id.trim(), ...payload })
      }
      onSave()
      onClose()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal open onClose={onClose} title={material ? "EDIT MATERIAL" : "NEW MATERIAL"} width={600}>
      <div className="flex flex-col gap-3">
        {!material && (
          <div>
            <label className="nb-label">MATERIAL ID</label>
            <input className="nb-input" value={id} onChange={e => setId(e.target.value)} placeholder="e.g. vintage_anime" />
          </div>
        )}
        <div>
          <label className="nb-label">NAME</label>
          <input className="nb-input" value={name} onChange={e => setName(e.target.value)} placeholder="Display Name" />
        </div>
        <div>
          <label className="nb-label">STYLE INSTRUCTION *</label>
          <textarea className="nb-input" rows={3} value={styleInstruction} onChange={e => setStyleInstruction(e.target.value)} placeholder="Detailed prompt for style..." />
        </div>
        <div>
          <label className="nb-label">NEGATIVE PROMPT</label>
          <input className="nb-input" value={negativePrompt} onChange={e => setNegativePrompt(e.target.value)} placeholder="Optional" />
        </div>
        <div>
          <label className="nb-label">SCENE PREFIX</label>
          <input className="nb-input" value={scenePrefix} onChange={e => setScenePrefix(e.target.value)} placeholder="Optional text prepended to prompts" />
        </div>
        <div>
          <label className="nb-label">LIGHTING</label>
          <input className="nb-input" value={lighting} onChange={e => setLighting(e.target.value)} placeholder="Optional lighting rules" />
        </div>
        {error && <div className="text-red-500 text-xs font-bold">{error}</div>}
        <div className="flex justify-end gap-2 mt-2">
          <button onClick={onClose} className="nb-btn nb-btn-ghost">Cancel</button>
          <button onClick={handleSave} disabled={loading} className="nb-btn nb-btn-primary bg-black text-white">
            {loading ? 'Saving...' : 'Save Material'}
          </button>
        </div>
      </div>
    </Modal>
  )
}
