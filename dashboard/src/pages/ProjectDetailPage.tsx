import { useState, useEffect, useCallback } from 'react'
import { fetchAPI, postAPI, deleteAPI } from '../api/client'
import { useWebSocket } from '../api/useWebSocket'
import type { Project, Character, Video, Scene } from '../types'
import Modal from '../components/shared/Modal'

interface Props {
  projectId: string
  onBack: () => void
  onRefresh?: () => void
}

import { PipelineProgressBanner } from '../components/projects/ui'
import { OverviewSection } from '../components/projects/sections/OverviewSection'
import { AssetsSection } from '../components/projects/sections/AssetsSection'
import { VideosSection } from '../components/projects/sections/VideosSection'
import { ScenesSection } from '../components/projects/sections/ScenesSection'
import { ProjectChatPanel } from '../components/projects/ProjectChatPanel'

// ---- Main ----
export default function ProjectDetailPage({ projectId, onBack, onRefresh }: Props) {
  const [project, setProject] = useState<Project | null>(null)
  const [characters, setCharacters] = useState<Character[]>([])
  const [videos, setVideos] = useState<Video[]>([])
  const [selectedVideoId, setSelectedVideoId] = useState('')
  const [loading, setLoading] = useState(true)
  const [sceneCounts, setSceneCounts] = useState<Record<string, number>>({})
  const [pipelineLoading, setPipelineLoading] = useState<string | false>(false)
  const [pipelineModalOpen, setPipelineModalOpen] = useState(false)
  const [refreshScenesTrigger, setRefreshScenesTrigger] = useState(0)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)

  const [config, setConfig] = useState(() => {
    try {
      const saved = localStorage.getItem(`project_config_${projectId}`)
      if (saved) return JSON.parse(saved)
    } catch(e){}
    return { minChars: 2, maxChars: 5, minLocs: 1, maxLocs: 3, minOthers: 0, maxOthers: 8, videosCount: 1, scenesPerVideo: 5, charMode: 'AUTO', locMode: 'AUTO', otherMode: 'MANUAL', ttsTemplate: null, videoLang: 'vi' }
  })

  useEffect(() => {
    localStorage.setItem(`project_config_${projectId}`, JSON.stringify(config))
  }, [projectId, config])

  const { lastEvent } = useWebSocket()

  async function runFullPipeline(mode: 'overwrite' | 'fill') {
    setPipelineModalOpen(false)
    if (!project?.story && !project?.description) {
      alert("Missing story: Please add a story or description to the project first.")
      return
    }
    
    try {
      if (mode === 'overwrite') {
        setCharacters([])
        setVideos([])
        setSceneCounts({})
        setSelectedVideoId('')
      }
      
      let currentVideos = [...videos]
      if (mode === 'overwrite' || currentVideos.length === 0) {
        setPipelineLoading('Extracting Videos...')
        const vidRes = await postAPI<{ success: boolean; count: number; videos: Video[] }>(`/api/projects/${project.id}/auto-generate-videos`, { num_videos: config.videosCount })
        if (vidRes && vidRes.videos && vidRes.videos.length > 0) {
          currentVideos = vidRes.videos
          setSelectedVideoId(currentVideos[0].id)
        }
        await fetchAll()
      }

      let currentChars = [...characters]
      if (mode === 'overwrite' || currentChars.length === 0) {
        setPipelineLoading('Extracting Assets...')
        const extRes = await postAPI<{ success: boolean; count: number; entities: Character[] }>(`/api/projects/${project.id}/auto-extract-assets`, {
          min_characters: config.charMode === 'AUTO' ? null : config.minChars, max_characters: config.charMode === 'AUTO' ? null : config.maxChars,
          min_locations: config.locMode === 'AUTO' ? null : config.minLocs, max_locations: config.locMode === 'AUTO' ? null : config.maxLocs,
          min_visual_assets: config.otherMode === 'AUTO' ? null : config.minOthers, max_visual_assets: config.otherMode === 'AUTO' ? null : config.maxOthers
        })
        if (extRes && extRes.entities) currentChars = extRes.entities
        await fetchAll()
      }

      const missingRefs = currentChars.filter(c => !c.media_id)
      if (missingRefs.length > 0) {
        setPipelineLoading('Generating Refs...')
        const refReqs = missingRefs.map(c => ({ type: 'GENERATE_CHARACTER_IMAGE', character_id: c.id, project_id: project.id }))
        await postAPI('/api/requests/batch', { requests: refReqs })

        await new Promise<void>((resolve, reject) => {
          const pollRefs = async () => {
            try {
              const status = await fetchAPI<{ done: boolean }>(`/api/requests/batch-status?project_id=${project.id}&type=GENERATE_CHARACTER_IMAGE`)
              fetchAll()
              if (status.done) resolve()
              else setTimeout(pollRefs, 8000)
            } catch (e) { reject(e) }
          }
          setTimeout(pollRefs, 5000)
        })
      }

      let activeScenes: Scene[] = []
      
      setPipelineLoading('Writing Scripts...')
      for (const video of currentVideos) {
        let videoScenes: Scene[] = []
        const currentScenesCount = sceneCounts[video.id] || 0
        if (mode === 'overwrite' || currentScenesCount === 0) {
          const sceneRes = await postAPI<{ success: boolean; count: number; scenes: Scene[] }>(`/api/videos/${video.id}/auto-generate-scenes`, { num_scenes: config.scenesPerVideo })
          if (sceneRes && sceneRes.scenes) videoScenes = sceneRes.scenes
        } else {
          try {
            videoScenes = await fetchAPI<Scene[]>(`/api/scenes?video_id=${video.id}`)
          } catch(e) {}
        }
        activeScenes.push(...videoScenes)
      }
      
      await fetchAll()
      setRefreshScenesTrigger(prev => prev + 1)

      if (activeScenes.length > 0) {
        const orientation = project.orientation as 'HORIZONTAL' | 'VERTICAL'

        setPipelineLoading('Generating Images...')
        let scenesForImage = activeScenes
        if (mode === 'fill') {
           scenesForImage = activeScenes.filter(s => {
             const status = orientation === 'HORIZONTAL' ? s.horizontal_image_status : s.vertical_image_status
             return status !== 'COMPLETED'
           })
        }
        
        if (scenesForImage.length > 0) {
          const imgRequests = scenesForImage.map(s => ({ type: 'GENERATE_IMAGE', scene_id: s.id, project_id: project.id, video_id: s.video_id, orientation }))
          await postAPI('/api/requests/batch', { requests: imgRequests })

          await new Promise<void>((resolve, reject) => {
            const pollImages = async () => {
              try {
                const status = await fetchAPI<{ done: boolean }>(`/api/requests/batch-status?project_id=${project.id}&type=GENERATE_IMAGE`)
                setRefreshScenesTrigger(prev => prev + 1)
                if (status.done) resolve()
                else setTimeout(pollImages, 8000)
              } catch (e) { reject(e) }
            }
            setTimeout(pollImages, 5000)
          })
        }

        setPipelineLoading('Generating Videos...')
        let scenesForVideo = activeScenes
        if (mode === 'fill') {
           scenesForVideo = activeScenes.filter(s => {
             const status = orientation === 'HORIZONTAL' ? s.horizontal_video_status : s.vertical_video_status
             return status !== 'COMPLETED'
           })
        }

        if (scenesForVideo.length > 0) {
          const vidRequests = scenesForVideo.map(s => ({ type: 'GENERATE_VIDEO', scene_id: s.id, project_id: project.id, video_id: s.video_id, orientation }))
          await postAPI('/api/requests/batch', { requests: vidRequests })

          await new Promise<void>((resolve, reject) => {
            const pollVideos = async () => {
              try {
                const vStatus = await fetchAPI<{ done: boolean }>(`/api/requests/batch-status?project_id=${project.id}&type=GENERATE_VIDEO`)
                setRefreshScenesTrigger(prev => prev + 1)
                if (vStatus.done) resolve()
                else setTimeout(pollVideos, 8000)
              } catch (e) { reject(e) }
            }
            setTimeout(pollVideos, 5000)
          })
        }
      }

    } catch (e) {
      console.error(e)
    } finally {
      setPipelineLoading(false)
    }
  }

  const handleCancelPipeline = async () => {
    if (!confirm("Are you sure you want to stop the pipeline? This will cancel all pending processing requests.")) return;
    try {
      await postAPI(`/api/requests/batch/cancel?project_id=${projectId}`, {});
      setPipelineLoading(false);
      fetchAll();
      setRefreshScenesTrigger(prev => prev + 1);
    } catch(e) {
      console.error("Failed to cancel pipeline", e);
    }
  }

  const handleDeleteProject = async () => {
    try {
      await deleteAPI(`/api/projects/${projectId}`)
      if (onRefresh) onRefresh()
      onBack()
    } catch (e) {
      console.error(e)
      alert("Failed to delete project")
    }
  }

  const fetchAll = useCallback(async () => {
    try {
      const [proj, chars, vids] = await Promise.all([
        fetchAPI<Project>(`/api/projects/${projectId}`),
        fetchAPI<Character[]>(`/api/projects/${projectId}/characters`),
        fetchAPI<Video[]>(`/api/videos?project_id=${projectId}`),
      ])
      setProject(proj)
      setCharacters(chars)
      setVideos(vids)
      const counts: Record<string, number> = {}
      await Promise.all(vids.map(async v => {
        try {
          const scenes = await fetchAPI<Scene[]>(`/api/scenes?video_id=${v.id}`)
          counts[v.id] = scenes.length
        } catch { counts[v.id] = 0 }
      }))
      setSceneCounts(counts)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }, [projectId])

  useEffect(() => { fetchAll() }, [fetchAll])

  useEffect(() => {
    if (!lastEvent) return
    if (
      lastEvent.type === 'project_created' || 
      lastEvent.type === 'project_updated' || 
      lastEvent.type === 'request_update'
    ) {
      fetchAll()
    }
    if (onRefresh) onRefresh()
  }, [lastEvent, fetchAll, onRefresh])

  if (loading || !project) {
    return <div className="text-[11px] font-bold" style={{ color: 'var(--muted)' }}>Loading project...</div>
  }

  return (
    <div className="flex items-start gap-6 pb-12 w-full">
      {/* Main Content Column */}
      <div className="flex flex-col gap-6 flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center gap-3">
        <button onClick={onBack} className="nb-btn nb-btn-ghost">← Back</button>
        <h1 className="font-black text-lg truncate" style={{ color: 'var(--text)' }}>{project.name}</h1>
        <span className="nb-badge">{project.status}</span>
        
        <button 
          onClick={() => setDeleteConfirmOpen(true)}
          className="nb-btn ml-auto transition-colors"
          style={{ background: 'var(--red)', color: 'white', borderColor: 'var(--border)' }}
          title="Delete Project"
        >
          <span className="text-[11px] font-bold uppercase flex items-center gap-1.5">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
            Delete
          </span>
        </button>
      </div>

      <div className="flex flex-col gap-8">
        <PipelineProgressBanner currentStage={pipelineLoading} onCancel={handleCancelPipeline} />

        <OverviewSection project={project} config={config} setConfig={setConfig} onRefresh={fetchAll} onOpenPipelineModal={() => setPipelineModalOpen(true)} pipelineLoading={pipelineLoading} />

        <div className="nb-divider" />
        <AssetsSection projectId={projectId} characters={characters} config={config} onRefresh={fetchAll} />

        <div className="nb-divider" />
        <VideosSection projectId={projectId} videos={videos} selectedVideoId={selectedVideoId} config={config} onSelectVideo={setSelectedVideoId} onRefresh={fetchAll} getSceneCount={id => sceneCounts[id] ?? 0} pipelineOrientation={project.orientation} />

        {selectedVideoId && (
          <>
            <div className="nb-divider" />
            <ScenesSection project={project} videoId={selectedVideoId} characters={characters} config={config} onSceneCountsChange={counts => setSceneCounts(prev => ({ ...prev, [selectedVideoId]: counts.length }))} pipelineOrientation={project.orientation} refreshTrigger={refreshScenesTrigger} />
          </>
        )}

        <Modal open={pipelineModalOpen} onClose={() => setPipelineModalOpen(false)} title="FULL-THROTTLE PIPELINE">
          <div className="flex flex-col gap-4">
            <div className="text-[12px] font-bold" style={{ color: 'var(--text)' }}>
              Choose how you want to run the pipeline:
            </div>
            
            <button onClick={() => runFullPipeline('overwrite')} className="nb-btn nb-btn-primary flex flex-col items-start gap-1 p-3 h-auto" style={{ background: 'var(--red)', color: 'white', borderColor: 'var(--red)', boxShadow: '4px 4px 0px rgba(0,0,0,0.3)' }}>
              <div className="font-black uppercase tracking-wider">Option 1: Overwrite All</div>
              <div className="text-[11px] font-semibold" style={{ opacity: 0.9, textAlign: 'left', textTransform: 'none' }}>
                Deletes all existing assets, scenes, and media. Regenerates everything from scratch.
              </div>
            </button>

            <button onClick={() => runFullPipeline('fill')} className="nb-btn nb-btn-primary flex flex-col items-start gap-1 p-3 h-auto" style={{ background: 'var(--green)', color: 'white', borderColor: 'var(--green)', boxShadow: '4px 4px 0px rgba(0,0,0,0.3)' }}>
              <div className="font-black uppercase tracking-wider">Option 2: Fill Missing Data</div>
              <div className="text-[11px] font-semibold" style={{ opacity: 0.9, textAlign: 'left', textTransform: 'none' }}>
                Keeps existing data intact. Only generates new assets/scenes if none exist, and only generates media for incomplete scenes.
              </div>
            </button>
          </div>
        </Modal>

        <Modal open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)} title="DELETE PROJECT" width={400}>
          <div className="flex flex-col gap-4">
            <p className="text-[11px] font-semibold" style={{ color: 'var(--muted)' }}>
              Are you sure you want to delete "{project.name}"? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setDeleteConfirmOpen(false)} className="nb-btn nb-btn-ghost">Cancel</button>
              <button onClick={handleDeleteProject} className="nb-btn nb-btn-danger">
                Delete
              </button>
            </div>
          </div>
        </Modal>
      </div>
      </div>

      {/* Chat Agent Column */}
      <div className="w-1/3 min-w-[300px] max-w-[400px] sticky top-4 self-start h-[calc(100vh-6rem)]">
        <ProjectChatPanel projectId={projectId} uiContext={{ pipelineOrientation: project.orientation, config }} />
      </div>
    </div>
  )
}