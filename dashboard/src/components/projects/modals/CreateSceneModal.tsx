import { useState, useEffect } from 'react'
import { postAPI } from '../../../api/client'
import type { Scene, Character, ChainType } from '../../../types'
import Modal from '../../shared/Modal'

export function CreateSceneModal({ open, videoId, existingScenes, characters, onClose, onCreated }: {
  open: boolean; videoId: string; existingScenes: Scene[]; characters: Character[]
  onClose: () => void; onCreated: () => void
}) {
  const [prompt, setPrompt] = useState('')
  const [chainType, setChainType] = useState<ChainType>('ROOT')
  const [selectedChars, setSelectedChars] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function reset() { setPrompt(''); setChainType('ROOT'); setSelectedChars([]); setError('') }
  useEffect(() => { if (open) reset() }, [open])

  async function handleCreate() {
    if (!prompt.trim()) { setError('Prompt is required'); return }
    setLoading(true)
    try {
      const nextOrder = existingScenes.length
      const parentId = chainType !== 'ROOT' && existingScenes.length > 0 ? existingScenes[existingScenes.length - 1].id : null
      await postAPI<Scene>('/api/scenes', {
        video_id: videoId, display_order: nextOrder, prompt: prompt.trim(), chain_type: chainType,
        character_names: selectedChars.length > 0 ? JSON.stringify(selectedChars) : null,
        ...(parentId ? { parent_scene_id: parentId } : {}),
      })
      reset()
      onCreated()
      onClose()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to create scene')
    } finally { setLoading(false) }
  }

  function toggleChar(name: string) { setSelectedChars(prev => prev.includes(name) ? prev.filter(n => n !== name) : [...prev, name]) }

  return (
    <Modal open={open} onClose={onClose} title="NEW SCENE" width={520}>
      <div className="flex flex-col gap-3">
        <div>
          <label className="nb-label">PROMPT *</label>
          <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
            placeholder="Describe the scene — what happens, who appears, what is the action..." rows={4}
            className="nb-input resize-y" autoFocus />
        </div>
        <div>
          <label className="nb-label">CHAIN TYPE</label>
          <select value={chainType} onChange={e => setChainType(e.target.value as ChainType)} className="nb-select w-full">
            <option value="ROOT">ROOT (first scene)</option>
            <option value="CONTINUATION">CONTINUATION (chain from previous)</option>
            <option value="INSERT">INSERT (cutaway/close-up)</option>
          </select>
          {chainType !== 'ROOT' && existingScenes.length === 0 && (
            <div className="text-[11px] font-bold mt-1" style={{ color: 'var(--yellow)' }}>No previous scenes — will be created as ROOT</div>
          )}
        </div>
        {characters.length > 0 && (
          <div>
            <label className="nb-label">ENTITIES (optional)</label>
            <div className="flex flex-wrap gap-1">
              {characters.map(ch => (
                <button key={ch.id} onClick={() => toggleChar(ch.name)} className="text-[11px] font-black px-3 py-1.5 uppercase transition-colors"
                  style={{
                    background: selectedChars.includes(ch.name) ? 'var(--text)' : 'var(--bg)',
                    color: selectedChars.includes(ch.name) ? '#fff' : 'var(--text)',
                    border: `2px solid var(--border)`,
                    cursor: 'pointer',
                  }}>
                  {ch.name}
                </button>
              ))}
            </div>
          </div>
        )}
        {error && <div className="text-[11px] font-bold" style={{ color: 'var(--red)' }}>{error}</div>}
        <div className="flex justify-end gap-2 mt-2">
          <button onClick={onClose} className="nb-btn nb-btn-ghost">Cancel</button>
          <button onClick={handleCreate} disabled={loading} className="nb-btn nb-btn-accent">
            {loading ? 'Creating...' : 'Create Scene'}
          </button>
        </div>
      </div>
    </Modal>
  )
}
