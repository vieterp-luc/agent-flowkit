import { useState, useEffect } from 'react'
import { postAPI } from '../../../api/client'
import type { Character, EntityType } from '../../../types'
import Modal from '../../shared/Modal'

export function CreateEntityModal({ open, projectId, onClose, onCreated }: {
  open: boolean; projectId: string; onClose: () => void; onCreated: () => void
}) {
  const [name, setName] = useState('')
  const [entityType, setEntityType] = useState<EntityType>('character')
  const [description, setDescription] = useState('')
  const [voiceDesc, setVoiceDesc] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function reset() { setName(''); setEntityType('character'); setDescription(''); setVoiceDesc(''); setError('') }
  useEffect(() => { if (open) reset() }, [open])

  async function handleCreate() {
    if (!name.trim()) { setError('Name is required'); return }
    setLoading(true)
    try {
      const char = await postAPI<Character>('/api/characters', {
        name: name.trim(),
        entity_type: entityType,
        description: description.trim() || null,
        voice_description: voiceDesc.trim() || null,
      })
      await postAPI(`/api/projects/${projectId}/characters/${char.id}`, {})
      reset()
      onCreated()
      onClose()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to create entity')
    } finally { setLoading(false) }
  }

  return (
    <Modal open={open} onClose={onClose} title="NEW ENTITY">
      <div className="flex flex-col gap-3">
        <div>
          <label className="nb-label">NAME *</label>
          <input type="text" value={name} onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleCreate()}
            placeholder="Character or location name"
            className="nb-input" autoFocus />
        </div>
        <div>
          <label className="nb-label">TYPE</label>
          <select value={entityType} onChange={e => setEntityType(e.target.value as EntityType)} className="nb-select w-full">
            <option value="character">Character</option>
            <option value="location">Location</option>
            <option value="creature">Creature</option>
            <option value="visual_asset">Visual Asset</option>
            <option value="generic_troop">Generic Troop</option>
            <option value="faction">Faction</option>
          </select>
        </div>
        <div>
          <label className="nb-label">APPEARANCE (for ref image)</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)}
            placeholder="Describe appearance only — what it looks like..."
            rows={3} className="nb-input resize-y" />
        </div>
        <div>
          <label className="nb-label">VOICE DESCRIPTION</label>
          <input type="text" value={voiceDesc} onChange={e => setVoiceDesc(e.target.value)}
            placeholder="Soft curious childlike voice, slight accent..." className="nb-input" />
        </div>
        {error && <div className="text-[11px] font-bold" style={{ color: 'var(--red)' }}>{error}</div>}
        <div className="flex justify-end gap-2 mt-2">
          <button onClick={onClose} className="nb-btn nb-btn-ghost">Cancel</button>
          <button onClick={handleCreate} disabled={loading} className="nb-btn nb-btn-accent">
            {loading ? 'Creating...' : 'Create & Link'}
          </button>
        </div>
      </div>
    </Modal>
  )
}
