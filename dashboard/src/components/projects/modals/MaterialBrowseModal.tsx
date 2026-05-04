import { useState, useEffect, useRef } from 'react'
import { fetchAPI, deleteAPI, patchAPI } from '../../../api/client'
import Modal from '../../shared/Modal'

export function MaterialBrowseModal({ open, onClose, onSelect }: { open: boolean, onClose: () => void, onSelect: (m: string) => void }) {
  const [materials, setMaterials] = useState<any[]>([])
  
  useEffect(() => {
    if (open && materials.length === 0) {
      fetchAPI<any[]>('/api/materials').then(setMaterials).catch(console.error)
    }
  }, [open, materials.length])

  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isUploading, setIsUploading] = useState(false)

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
      
      const newMat = await res.json()
      setMaterials(prev => [...prev, newMat])
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (err) {
      console.error(err)
      alert("Failed to extract material style from image.")
    } finally {
      setIsUploading(false)
    }
  }

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    if (!confirm("Delete this material?")) return
    try {
      await deleteAPI(`/api/materials/${id}`)
      setMaterials(prev => prev.filter(m => m.id !== id))
    } catch (err) {
      console.error(err)
      alert("Failed to delete material")
    }
  }

  const [editingMat, setEditingMat] = useState<any | null>(null)
  
  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingMat) return
    try {
      const res = await patchAPI<any>(`/api/materials/${editingMat.id}`, editingMat)
      setMaterials(prev => prev.map(m => m.id === res.id ? res : m))
      setEditingMat(null)
    } catch(err) {
      console.error(err)
      alert("Failed to update material")
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="SELECT MATERIAL STYLE" width={960}>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 py-2">
        <div onClick={() => !isUploading && fileInputRef.current?.click()} className="nb-card flex flex-col overflow-hidden group cursor-pointer hover:-translate-y-1 transition-transform relative">
          <div className="aspect-square w-full border-b flex items-center justify-center bg-[var(--surface)]" style={{ borderColor: 'var(--border)' }}>
            {isUploading ? (
              <span className="animate-pulse text-xs font-bold">EXTRACTING...</span>
            ) : (
              <span className="text-4xl font-light" style={{ color: 'var(--muted)' }}>+</span>
            )}
          </div>
          <div className="p-2.5 flex flex-col justify-center bg-[var(--surface)]">
            <div className="text-[12px] font-black uppercase truncate text-center" style={{ color: 'var(--text)' }}>Add</div>
          </div>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept="image/*" 
            className="hidden" 
          />
        </div>

        {materials.map(mat => (
          <div key={mat.id} onClick={() => onSelect(mat.id)} className="nb-card flex flex-col overflow-hidden group cursor-pointer hover:-translate-y-1 transition-transform">
            <div className="aspect-square w-full border-b relative overflow-hidden" style={{ borderColor: 'var(--border)' }}>
              <img 
                src={`/materials/${mat.id}_preview.png`} 
                alt={mat.name} 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" 
                onError={(e) => { (e.target as HTMLImageElement).src = 'https://placehold.co/400x400/222/555?text=Preview' }} 
              />
              <div className="absolute top-2 right-2 z-10">
                {mat.is_builtin ? <span className="text-[8px] font-black uppercase px-1.5 py-0.5 rounded-sm shadow-[2px_2px_0px_#000]" style={{ background: 'var(--text)', color: 'var(--bg)', border: 'var(--border-w) solid var(--border)' }}>BUILT-IN</span> : <span className="text-[8px] font-black uppercase px-1.5 py-0.5 rounded-sm shadow-[2px_2px_0px_#000]" style={{ background: 'var(--yellow)', color: 'black', border: 'var(--border-w) solid var(--border)' }}>USER-UPLOAD</span>}
              </div>
              {!mat.is_builtin && (
                <div className="absolute top-2 left-2 flex gap-1 z-10">
                  <button onClick={(e) => { e.stopPropagation(); setEditingMat(mat) }} className="bg-blue-500 text-white p-1 rounded hover:bg-blue-600 text-[10px] shadow-[2px_2px_0px_#000]" style={{ border: 'var(--border-w) solid var(--border)' }}>EDIT</button>
                  <button onClick={(e) => handleDelete(e, mat.id)} className="bg-red-500 text-white p-1 rounded hover:bg-red-600 text-[10px] shadow-[2px_2px_0px_#000]" style={{ border: 'var(--border-w) solid var(--border)' }}>DEL</button>
                </div>
              )}
            </div>
            <div className="p-2.5 flex flex-col justify-center bg-[var(--surface)]">
              <div className="text-[12px] font-black uppercase truncate text-center" style={{ color: 'var(--text)' }} title={mat.name}>{mat.name}</div>
            </div>
          </div>
        ))}
      </div>
      {editingMat && (
        <Modal open={true} onClose={() => setEditingMat(null)} title="EDIT MATERIAL STYLE" width={600}>
          <form onSubmit={handleUpdate} className="flex flex-col gap-3 py-2">
            <div>
              <label className="nb-label">NAME</label>
              <input type="text" className="nb-input w-full" value={editingMat.name} onChange={e => setEditingMat({...editingMat, name: e.target.value})} required />
            </div>
            <div>
              <label className="nb-label">STYLE INSTRUCTION</label>
              <textarea className="nb-input w-full" rows={4} value={editingMat.style_instruction} onChange={e => setEditingMat({...editingMat, style_instruction: e.target.value})} required />
            </div>
            <div>
              <label className="nb-label">NEGATIVE PROMPT</label>
              <textarea className="nb-input w-full" rows={2} value={editingMat.negative_prompt || ''} onChange={e => setEditingMat({...editingMat, negative_prompt: e.target.value})} />
            </div>
            <div>
              <label className="nb-label">SCENE PREFIX</label>
              <textarea className="nb-input w-full" rows={2} value={editingMat.scene_prefix || ''} onChange={e => setEditingMat({...editingMat, scene_prefix: e.target.value})} />
            </div>
            <div>
              <label className="nb-label">LIGHTING</label>
              <input type="text" className="nb-input w-full" value={editingMat.lighting || ''} onChange={e => setEditingMat({...editingMat, lighting: e.target.value})} required />
            </div>
            <div className="flex justify-end gap-2 mt-4">
              <button type="button" className="nb-btn nb-btn-ghost" onClick={() => setEditingMat(null)}>CANCEL</button>
              <button type="submit" className="nb-btn nb-btn-primary">SAVE CHANGES</button>
            </div>
          </form>
        </Modal>
      )}
    </Modal>
  )
}
