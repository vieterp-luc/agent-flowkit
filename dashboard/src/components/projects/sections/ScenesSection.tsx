import { useState, useEffect, useRef, useCallback } from 'react'
import { fetchAPI, patchAPI, postAPI } from '../../../api/client'
import type { Project, Scene, Character } from '../../../types'
import { ChainBadge, StatusDot, SceneProgressBar } from '../ui'
import { SceneDetailModal } from '../modals/SceneDetailModal'
import { CreateSceneModal } from '../modals/CreateSceneModal'
import { parseCharNames } from '../utils'

export function ScenesSection({ project, videoId, characters, config, onSceneCountsChange, pipelineOrientation, refreshTrigger }: { project: Project; videoId: string; characters: Character[]; config: any; onSceneCountsChange?: (scenes: Scene[]) => void; pipelineOrientation: 'VERTICAL' | 'HORIZONTAL'; refreshTrigger?: number }) {
  const [scenes, setScenes] = useState<Scene[]>([])
  const [loading, setLoading] = useState(false)
  const [detailScene, setDetailScene] = useState<Scene | null>(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [filter, setFilter] = useState('')
  const [genScenesLoading, setGenScenesLoading] = useState<string | false>(false)

  async function handleAutoGenerateScenes() {
    if (!project.story && !project.description) {
      alert("Missing story: Please add a story or description to the project first.")
      return
    }
    if (characters.length === 0) {
      alert("Missing assets: Please extract or create entities (characters/locations) first.")
      return
    }
    const missingRefs = characters.filter(c => !c.media_id)
    if (missingRefs.length > 0) {
      alert(`Missing reference images for ${missingRefs.length} entities. Please generate all reference images before auto-generating scenes.`)
      return
    }

    try {
      setGenScenesLoading('Writing Script...')
      const sceneRes = await postAPI<{ success: boolean; count: number; scenes: Scene[] }>(`/api/videos/${videoId}/auto-generate-scenes`, { num_scenes: config.scenesPerVideo })
      load(videoId, true)

      if (sceneRes && sceneRes.scenes && sceneRes.scenes.length > 0) {
        const orientation = pipelineOrientation

        setGenScenesLoading('Generating Images...')
        const imgRequests = sceneRes.scenes.map(s => ({
          type: 'GENERATE_IMAGE',
          scene_id: s.id,
          project_id: project.id,
          video_id: videoId,
          orientation: orientation
        }))
        await postAPI('/api/requests/batch', { requests: imgRequests })

        await new Promise<void>((resolve, reject) => {
          const pollImages = async () => {
            try {
              const status = await fetchAPI<{ done: boolean }>(`/api/requests/batch-status?video_id=${videoId}&type=GENERATE_IMAGE`)
              load(videoId, true)
              if (status.done) resolve()
              else setTimeout(pollImages, 8000)
            } catch (e) { reject(e) }
          }
          setTimeout(pollImages, 5000)
        })

        setGenScenesLoading('Generating Videos...')
        const vidRequests = sceneRes.scenes.map(s => ({
          type: 'GENERATE_VIDEO',
          scene_id: s.id,
          project_id: project.id,
          video_id: videoId,
          orientation: orientation
        }))
        await postAPI('/api/requests/batch', { requests: vidRequests })

        await new Promise<void>((resolve, reject) => {
          const pollVideos = async () => {
            try {
              const vStatus = await fetchAPI<{ done: boolean }>(`/api/requests/batch-status?video_id=${videoId}&type=GENERATE_VIDEO`)
              load(videoId)
              if (vStatus.done) resolve()
              else setTimeout(pollVideos, 8000)
            } catch (e) { reject(e) }
          }
          setTimeout(pollVideos, 5000)
        })
      }
    } catch (e) {
      console.error(e)
    } finally {
      setGenScenesLoading(false)
    }
  }

  const [concatLoading, setConcatLoading] = useState<string | false>(false)

  async function handleConcatScenes() {
    if (!videoId || !project) return
    setConcatLoading('Upscaling Videos...')
    try {
      const orientation = pipelineOrientation

      const upscaleRequests = scenes.map(s => ({ type: 'UPSCALE_VIDEO', scene_id: s.id, project_id: project.id, video_id: videoId, orientation }))
      await postAPI('/api/requests/batch', { requests: upscaleRequests })

      await new Promise<void>((resolve, reject) => {
        const pollUpscales = async () => {
          try {
            const vStatus = await fetchAPI<{ done: boolean }>(`/api/requests/batch-status?video_id=${videoId}&type=UPSCALE_VIDEO`)
            load(videoId, true)
            if (vStatus.done) resolve()
            else setTimeout(pollUpscales, 8000)
          } catch (e) { reject(e) }
        }
        setTimeout(pollUpscales, 5000)
      })

      setConcatLoading('Concatenating...')
      await postAPI('/api/chat', { 
        messages: [{ role: 'user', content: `/fk-concat ${videoId}` }] 
      })

    } catch (e) {
      console.error(e)
    } finally {
      setConcatLoading(false)
      load(videoId, true)
    }
  }

  const allVideosReady = scenes.length > 0 && scenes.every(s => {
    const vidStatus = pipelineOrientation === 'HORIZONTAL' ? s.horizontal_video_status : s.vertical_video_status;
    const upStatus = pipelineOrientation === 'HORIZONTAL' ? s.horizontal_upscale_status : s.vertical_upscale_status;
    return (vidStatus === 'COMPLETED' || upStatus === 'COMPLETED') && 
           s.horizontal_video_status !== 'FAILED' && s.vertical_video_status !== 'FAILED' &&
           s.horizontal_upscale_status !== 'FAILED' && s.vertical_upscale_status !== 'FAILED';
  });

  const [draggedSceneId, setDraggedSceneId] = useState<string | null>(null)
  const [originalScenes, setOriginalScenes] = useState<Scene[]>([])

  const onSceneCountsChangeRef = useRef(onSceneCountsChange)
  useEffect(() => {
    onSceneCountsChangeRef.current = onSceneCountsChange
  }, [onSceneCountsChange])

  const load = useCallback((vid: string, silent = false) => {
    if (!vid) { setScenes([]); return }
    if (!silent) setLoading(true)
    fetchAPI<Scene[]>(`/api/scenes?video_id=${vid}`)
      .then(s => { setScenes(s); if (onSceneCountsChangeRef.current) onSceneCountsChangeRef.current(s) })
      .catch(console.error)
      .finally(() => { if (!silent) setLoading(false) })
  }, [])

  useEffect(() => { load(videoId) }, [videoId, load])

  const prevTrigger = useRef(refreshTrigger)
  useEffect(() => {
    if (refreshTrigger !== prevTrigger.current) {
      prevTrigger.current = refreshTrigger
      if (refreshTrigger && refreshTrigger > 0) {
        load(videoId, true)
      }
    }
  }, [refreshTrigger, videoId, load])

  function syncOrderToServer(currentScenes: Scene[]) {
    const promises = []
    for (let i = 0; i < currentScenes.length; i++) {
      if (currentScenes[i].display_order !== i) {
        currentScenes[i] = { ...currentScenes[i], display_order: i }
        promises.push(patchAPI(`/api/scenes/${currentScenes[i].id}`, { display_order: String(i) }))
      }
    }
    if (promises.length > 0) {
      Promise.all(promises).catch(console.error).finally(() => load(videoId, true))
    }
  }

  const [retryLoading, setRetryLoading] = useState<Set<string>>(new Set())

  async function handleRetry(sid: string) {
    if (!project || !videoId) return
    const scene = scenes.find(s => s.id === sid)
    if (!scene) return

    setRetryLoading(prev => {
      const next = new Set(prev)
      next.add(sid)
      return next
    })
    try {
      const orientation = pipelineOrientation

      const imgStatus = orientation === 'HORIZONTAL' ? scene.horizontal_image_status : scene.vertical_image_status;
      const vidStatus = orientation === 'HORIZONTAL' ? scene.horizontal_video_status : scene.vertical_video_status;
      const upStatus = orientation === 'HORIZONTAL' ? scene.horizontal_upscale_status : scene.vertical_upscale_status;

      let reqType = ''
      let patchField = ''
      if (imgStatus === 'FAILED') {
        reqType = 'GENERATE_IMAGE'
        patchField = orientation === 'HORIZONTAL' ? 'horizontal_image_status' : 'vertical_image_status'
      } else if (vidStatus === 'FAILED') {
        reqType = 'GENERATE_VIDEO'
        patchField = orientation === 'HORIZONTAL' ? 'horizontal_video_status' : 'vertical_video_status'
      } else if (upStatus === 'FAILED') {
        reqType = 'UPSCALE_VIDEO'
        patchField = orientation === 'HORIZONTAL' ? 'horizontal_upscale_status' : 'vertical_upscale_status'
      } else {
        reqType = 'REGENERATE_VIDEO'
        patchField = orientation === 'HORIZONTAL' ? 'horizontal_video_status' : 'vertical_video_status'
      }

      if (reqType) {
        await patchAPI(`/api/scenes/${sid}`, { [patchField]: 'PENDING' })

        await postAPI('/api/requests/batch', {
          requests: [{
            type: reqType,
            scene_id: sid,
            project_id: project.id,
            video_id: videoId,
            orientation,
            retry_count: 4
          }]
        })

        await new Promise<void>((resolve, reject) => {
          const pollStatus = async () => {
            try {
              const status = await fetchAPI<{ done: boolean }>(`/api/requests/batch-status?video_id=${videoId}&type=${reqType}`)
              load(videoId, true)
              if (status.done) resolve()
              else setTimeout(pollStatus, 8000)
            } catch (e) { reject(e) }
          }
          setTimeout(pollStatus, 5000)
        })
      } else {
        await patchAPI(`/api/scenes/${sid}`, { status: 'PENDING' })
      }
    } catch (e) {
      console.error(e)
    } finally {
      setRetryLoading(prev => {
        const next = new Set(prev)
        next.delete(sid)
        return next
      })
      load(videoId)
    }
  }

  if (!videoId) return null

  const filtered = scenes.filter(s => {
    if (!filter) return true
    const q = filter.toLowerCase()
    return (s.prompt ?? '').toLowerCase().includes(q) ||
      (s.narrator_text ?? '').toLowerCase().includes(q) ||
      parseCharNames(s.character_names).some(n => n.toLowerCase().includes(q))
  })

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="text-xl font-black uppercase tracking-wider" style={{ color: 'var(--text)' }}>
          SCENES <span className="text-lg font-bold" style={{ color: 'var(--muted)' }}>{loading ? '...' : `(${filtered.length}/${scenes.length})`}</span>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={filter}
            onChange={e => setFilter(e.target.value)}
            placeholder="Filter scenes..."
            className="nb-input"
          />
          <button onClick={handleAutoGenerateScenes} disabled={!!genScenesLoading} className="nb-btn nb-btn-primary" style={{ background: 'var(--yellow)', color: 'black', borderColor: 'black' }}>
            {genScenesLoading ? `✨ ${genScenesLoading}` : '✨ Auto-Generate Scenes'}
          </button>
          <button 
            onClick={handleConcatScenes} 
            disabled={!!concatLoading || !allVideosReady} 
            className="nb-btn nb-btn-primary" 
            style={{ 
              background: (!allVideosReady || !!concatLoading) ? 'var(--surface)' : 'var(--green)', 
              color: (!allVideosReady || !!concatLoading) ? 'var(--muted)' : 'white', 
              borderColor: (!allVideosReady || !!concatLoading) ? 'var(--border)' : 'var(--green)',
              cursor: (!allVideosReady || !!concatLoading) ? 'not-allowed' : 'pointer'
            }}
          >
            {concatLoading ? `🎬 ${concatLoading}` : '🎬 Concat all scenes'}
          </button>
          <button onClick={() => setCreateOpen(true)} className="nb-btn nb-btn-primary" style={{ background: 'var(--text)', color: '#fff' }}>
            + New Scene
          </button>
        </div>
      </div>

      {!loading && scenes.length > 0 && <SceneProgressBar scenes={scenes} />}

      <div>
        {loading ? (
          <div className="text-[11px] py-4 font-bold" style={{ color: 'var(--muted)' }}>Loading scenes...</div>
        ) : filtered.length === 0 ? (
          <div className="text-[11px] py-4 font-bold" style={{ color: 'var(--muted)' }}>
            {scenes.length === 0 ? 'No scenes in this video. Create one to begin.' : 'No scenes match your filter.'}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((scene) => {
              const charNames = parseCharNames(scene.character_names)
              
              const imgStatus = pipelineOrientation === 'HORIZONTAL' ? scene.horizontal_image_status : scene.vertical_image_status;
              const vidStatus = pipelineOrientation === 'HORIZONTAL' ? scene.horizontal_video_status : scene.vertical_video_status;
              const upStatus = pipelineOrientation === 'HORIZONTAL' ? scene.horizontal_upscale_status : scene.vertical_upscale_status;
              const hasError = imgStatus === 'FAILED' || vidStatus === 'FAILED' || upStatus === 'FAILED';
              const isProcessing = retryLoading.has(scene.id) || imgStatus === 'PROCESSING' || vidStatus === 'PROCESSING' || upStatus === 'PROCESSING';

              const thumbUrl = pipelineOrientation === 'HORIZONTAL' ? scene.horizontal_image_url : scene.vertical_image_url;
              const thumbMediaId = pipelineOrientation === 'HORIZONTAL' ? scene.horizontal_image_media_id : scene.vertical_image_media_id;
              const videoUrl = pipelineOrientation === 'HORIZONTAL' ? scene.horizontal_video_url : scene.vertical_video_url;
              const vidMediaId = pipelineOrientation === 'HORIZONTAL' ? scene.horizontal_video_media_id : scene.vertical_video_media_id;
              const upscaleUrl = pipelineOrientation === 'HORIZONTAL' ? scene.horizontal_upscale_url : scene.vertical_upscale_url;
              const upMediaId = pipelineOrientation === 'HORIZONTAL' ? scene.horizontal_upscale_media_id : scene.vertical_upscale_media_id;
              const displayVideo = upscaleUrl || videoUrl;
              const displayVideoMediaId = upscaleUrl ? upMediaId : vidMediaId;

              return (
                <div key={scene.id} className={`nb-card p-4 flex flex-col gap-3 cursor-pointer transition-all hover:-translate-y-1 hover:shadow-[6px_6px_0px_rgba(0,0,0,1)] ${draggedSceneId === scene.id ? 'opacity-30 border-dashed border-[3px] scale-95 shadow-none' : ''}`}
                  draggable
                  onDragStart={(e) => {
                    setDraggedSceneId(scene.id)
                    setOriginalScenes([...scenes])
                    e.dataTransfer.effectAllowed = 'move'
                    e.dataTransfer.setData('text/plain', scene.id)
                  }}
                  onDragEnter={(e) => {
                    e.preventDefault()
                    if (!draggedSceneId || draggedSceneId === scene.id) return
                    const sourceIdx = scenes.findIndex(s => s.id === draggedSceneId)
                    const targetIdx = scenes.findIndex(s => s.id === scene.id)
                    if (sourceIdx === -1 || targetIdx === -1) return
                    
                    const newScenes = [...scenes]
                    const [draggedItem] = newScenes.splice(sourceIdx, 1)
                    newScenes.splice(targetIdx, 0, draggedItem)
                    setScenes(newScenes)
                  }}
                  onDragEnd={() => {
                    setDraggedSceneId(curr => {
                      if (curr !== null) {
                        setScenes(originalScenes)
                      }
                      return null
                    })
                  }}
                  onDragOver={(e) => {
                    e.preventDefault()
                    e.dataTransfer.dropEffect = 'move'
                  }}
                  onDrop={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    setDraggedSceneId(null) 
                    syncOrderToServer(scenes)
                  }}
                  style={{ borderColor: hasError ? 'var(--red)' : 'var(--border)' }}
                  onClick={() => setDetailScene(scene)}>
                  
                  <div className="w-full rounded-sm overflow-hidden flex-shrink-0 relative" style={{ border: 'var(--border-w) solid var(--border)', aspectRatio: pipelineOrientation === 'HORIZONTAL' ? '16/9' : '9/16', background: 'var(--surface)' }}>
                    {displayVideo ? (
                      <video 
                        src={displayVideo} 
                        autoPlay loop muted playsInline 
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          const v = e.target as HTMLVideoElement;
                          if (!v.dataset.triedLocal && displayVideoMediaId) {
                            v.dataset.triedLocal = 'true';
                            v.src = `http://127.0.0.1:8100/api/flow/media-local/${displayVideoMediaId}`;
                            return;
                          }
                          
                          if (v.dataset.broken) return;
                          v.dataset.broken = 'true';
                          // Poster as broken image
                          v.poster = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiM1NTUiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTBweCIgZmlsbD0iI2FhYSIgZHRleHQtYW5jaG9yPSJtaWRkbGUiIGFsaWdubWVudC1iYXNlbGluZT0ibWlkZGxlIj5FeHBpcmVkLiBSZWNvdmVyaW5nLi4uPC90ZXh0Pjwvc3ZnPg==';
                        }}
                      />
                    ) : thumbUrl ? (
                      <img 
                        src={thumbUrl} 
                        className="w-full h-full object-cover" 
                        alt="Scene Thumbnail"
                        onError={(e) => {
                          const img = e.target as HTMLImageElement;
                          if (!img.dataset.triedLocal && thumbMediaId) {
                            img.dataset.triedLocal = 'true';
                            img.src = `http://127.0.0.1:8100/api/flow/media-local/${thumbMediaId}`;
                            return;
                          }
                          
                          if (img.dataset.broken) return;
                          img.dataset.broken = 'true';
                          img.src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiM1NTUiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTBweCIgZmlsbD0iI2FhYSIgZHRleHQtYW5jaG9yPSJtaWRkbGUiIGFsaWdubWVudC1iYXNlbGluZT0ibWlkZGxlIj5FeHBpcmVkLiBSZWNvdmVyaW5nLi4uPC90ZXh0Pjwvc3ZnPg==';
                        }}
                      />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center bg-[repeating-linear-gradient(45deg,transparent,transparent_10px,rgba(0,0,0,0.05)_10px,rgba(0,0,0,0.05)_20px)]">
                        <span className="text-[10px] font-black uppercase tracking-widest" style={{ color: 'var(--muted)' }}>
                          {imgStatus === 'PROCESSING' || vidStatus === 'PROCESSING' ? 'Processing...' : 'No Media'}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[14px] font-black" style={{ color: 'var(--text)' }}>#{scene.display_order + 1}</span>
                    <ChainBadge type={scene.chain_type} />
                    <div className="ml-auto flex items-center gap-1.5">
                      {isProcessing ? (
                        <span className="nb-badge px-2" style={{ background: 'var(--yellow)', color: 'black', borderColor: 'black', padding: '0.2rem 0.5rem' }}>PROCESSING...</span>
                      ) : (
                        <button 
                          onClick={(e) => { e.stopPropagation(); handleRetry(scene.id); }} 
                          disabled={retryLoading.has(scene.id) || !!genScenesLoading || !!concatLoading}
                          className={`nb-btn text-[9px] py-0.5 px-2 font-black uppercase transition-all disabled:opacity-50 disabled:cursor-not-allowed ${hasError ? 'hover:bg-red-50' : 'hover:bg-gray-50'}`} 
                          style={{ color: hasError ? 'var(--red)' : 'var(--text)', borderColor: hasError ? 'var(--red)' : 'var(--border)', background: 'transparent' }}
                        >
                          {retryLoading.has(scene.id) ? '...' : (hasError ? '↻ Retry' : '↻ Regen')}
                        </button>
                      )}
                      {hasError && !isProcessing && <span className="nb-badge" style={{ background: 'var(--red)', color: '#fff', borderColor: 'var(--red)' }}>FAILED</span>}
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-[10px] font-bold" style={{ color: 'var(--muted)' }}>
                    <span className="flex items-center gap-1.5"><StatusDot status={imgStatus} /> IMG</span>
                    <span className="flex items-center gap-1.5"><StatusDot status={vidStatus} /> VID</span>
                    <span className="flex items-center gap-1.5"><StatusDot status={upStatus} /> UPS</span>
                  </div>

                  {scene.narrator_text && (
                    <div className="text-[11px] p-2 italic rounded-sm shadow-[inset_2px_2px_0px_rgba(0,0,0,0.05)]" style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text)' }}>
                      "{scene.narrator_text}"
                    </div>
                  )}

                  {scene.prompt && (
                    <div className="text-[11px] font-mono leading-relaxed" style={{ color: 'var(--text)', whiteSpace: 'pre-wrap' }}>
                      {scene.prompt}
                    </div>
                  )}

                  {charNames.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-auto pt-2">
                      {charNames.map(name => (
                        <span key={name} className="nb-badge">{name}</span>
                      ))}
                    </div>
                  )}

                  <div className="flex items-center gap-1 mt-auto pt-3" style={{ borderTop: '2px solid var(--border)' }}>
                    <div className="flex items-center gap-1.5 text-[10px] font-bold" style={{ color: 'var(--muted)', cursor: 'grab' }} title="Drag to reorder" onClick={e => e.stopPropagation()}>
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
                      Drag to reorder
                    </div>
                    <span className="text-[10px] font-bold ml-auto" style={{ color: 'var(--muted)' }}>click for details</span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {detailScene && <SceneDetailModal scene={detailScene} onClose={() => setDetailScene(null)} onRetry={handleRetry} />}

      <CreateSceneModal open={createOpen} videoId={videoId} existingScenes={scenes} characters={characters} onClose={() => setCreateOpen(false)} onCreated={() => load(videoId)} />
    </div>
  )
}
