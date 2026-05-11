import { useState, useEffect } from 'react'
import { patchAPI, postAPI, fetchAPI } from '../../../api/client'
import type { Project } from '../../../types'
import EditableText from '../../projects/EditableText'
import { Badge } from '../ui'
import { MaterialBrowseModal } from '../modals/MaterialBrowseModal'
import { formatDate } from '../utils'

interface SocialCaption {
  fb_caption: string
  fb_hashtags: string
  tiktok_caption: string
  tiktok_hashtags: string
}

function CopyField({ label, value }: { label: string; value: string }) {
  const [copied, setCopied] = useState(false)
  function copy() {
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }
  return (
    <div className="flex flex-col gap-0.5">
      <div className="flex items-center justify-between">
        <span className="text-[9px] font-black uppercase tracking-wider" style={{ color: 'var(--muted)' }}>{label}</span>
        <button onClick={copy} className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: copied ? 'green' : 'var(--muted)', cursor: 'pointer' }}>
          {copied ? '✓' : 'Copy'}
        </button>
      </div>
      <div className="text-[11px] rounded px-2 py-1.5" style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text)', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
        {value}
      </div>
    </div>
  )
}

const VIDEO_LANGUAGES = [
  { code: 'vi', label: 'Tiếng Việt' },
  { code: 'en', label: 'English' },
  { code: 'ja', label: '日本語' },
  { code: 'ko', label: '한국어' },
  { code: 'zh', label: '中文' },
  { code: 'fr', label: 'Français' },
  { code: 'es', label: 'Español' },
]

export function OverviewSection({ project, config, setConfig, onRefresh, onOpenPipelineModal, pipelineLoading }: { project: Project; config: any; setConfig: (c: any) => void; onRefresh: () => void; onOpenPipelineModal?: () => void; pipelineLoading?: string | false }) {
  const [thumbLoading, setThumbLoading] = useState(false)
  const [models, setModels] = useState<Record<string, unknown> | null>(null)
  const [modelLoading, setModelLoading] = useState(false)
  const [showMaterialModal, setShowMaterialModal] = useState(false)
  const [ttsTemplates, setTtsTemplates] = useState<{ name: string; duration?: number }[]>([])

  const socialCaption: SocialCaption | null = (() => {
    try { return project.social_caption ? JSON.parse(project.social_caption) : null } catch { return null }
  })()

  async function patch(field: string, value: string) {
    await patchAPI(`/api/projects/${project.id}`, { [field]: value })
    onRefresh()
  }

  async function selectModel(section: 'image' | 'upscale', modelName: string) {
    if (modelLoading) return
    setModelLoading(true)
    try {
      const body = section === 'image'
        ? { image_models: { NANO_BANANA_PRO: modelName } }
        : { upscale_models: { VIDEO_RESOLUTION_4K: modelName } }
      const result = await patchAPI<{ models: Record<string, unknown> }>('/api/models', body)
      setModels(result.models)
    } catch (e) { console.error(e) }
    finally { setModelLoading(false) }
  }

  async function handleOpenOutput() {
    try {
      await postAPI(`/api/projects/${project.id}/open-output`, {})
    } catch (e) { console.error(e) }
  }

  async function handleGenThumbnail() {
    setThumbLoading(true)
    try {
      await postAPI(`/api/projects/${project.id}/generate-thumbnail`, {})
      onRefresh()
    } catch (e) { console.error(e) }
    finally { setThumbLoading(false) }
  }

  useEffect(() => {
    fetchAPI<Record<string, unknown>>('/api/models')
      .then(setModels)
      .catch(() => setModels(null))
    fetchAPI<{ name: string; duration?: number }[]>('/api/tts/templates')
      .then(setTtsTemplates)
      .catch(() => setTtsTemplates([]))
  }, [])

  const isImgGem = (models?.image_models as Record<string, string>)?.['NANO_BANANA_PRO'] === 'GEM_PIX_2'
  const isImgNar = (models?.image_models as Record<string, string>)?.['NANO_BANANA_PRO'] === 'NARWHAL'
  const isUp1080 = (models?.upscale_models as Record<string, string>)?.['VIDEO_RESOLUTION_4K'] === 'veo_3_1_upsampler_1080p'
  const isUp4k = (models?.upscale_models as Record<string, string>)?.['VIDEO_RESOLUTION_4K'] === 'veo_3_1_upsampler_4k'

  function modelBtn(active: boolean) {
    return {
      background: active ? 'var(--text)' : 'var(--surface)',
      color: active ? '#fff' : 'var(--text)',
      border: 'var(--border-w) solid var(--border)',
      cursor: modelLoading ? 'not-allowed' : 'pointer',
      opacity: modelLoading ? 0.5 : 1,
    }
  }

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
        {/* Left: project info */}
        <div className="nb-card p-5 flex flex-col gap-4">
          <div>
            <div className="nb-label">PROJECT NAME</div>
            <EditableText value={project.name} onSave={v => patch('name', v)} className="font-black text-base" />
          </div>
          <div>
            <div className="nb-label">STORY</div>
            <EditableText value={project.story ?? ''} onSave={v => patch('story', v)} multiline className="text-[11px]" />
          </div>
          <div>
            <div className="nb-label">DESCRIPTION</div>
            <EditableText value={project.description ?? ''} onSave={v => patch('description', v)} multiline className="text-[11px]" />
          </div>
          
          <div className="flex flex-col gap-2 mt-2">
            <div className="nb-label mb-0">THUMBNAIL</div>
            {project.thumbnail_url ? (
              <div className="overflow-hidden rounded-md" style={{ border: 'var(--border-w) solid var(--border)', aspectRatio: '9/16', maxHeight: 240 }}>
                <img src={project.thumbnail_url} alt="Thumbnail" className="w-full h-full object-cover" />
              </div>
            ) : (
              <div className="flex items-center justify-center rounded-md" style={{ background: 'var(--surface)', border: 'var(--border-w) solid var(--border)', aspectRatio: '9/16', maxHeight: 240, color: 'var(--muted)' }}>
                No thumbnail yet
              </div>
            )}
            <button onClick={handleGenThumbnail} disabled={thumbLoading} className="nb-btn nb-btn-ghost text-[10px] w-full mt-1">
              {thumbLoading ? 'Generating...' : 'Generate Thumbnail'}
            </button>
          </div>

          {socialCaption && (
            <div className="flex flex-col gap-2 mt-1">
              <div className="nb-label mb-0">📱 CAPTION MXH</div>
              <div className="flex flex-col gap-1.5">
                <div className="text-[9px] font-black uppercase tracking-wider" style={{ color: 'var(--blue)' }}>Facebook</div>
                <CopyField label="Caption" value={socialCaption.fb_caption} />
                <CopyField label="Hashtags" value={socialCaption.fb_hashtags} />
                <div className="text-[9px] font-black uppercase tracking-wider mt-1" style={{ color: 'var(--text)' }}>TikTok</div>
                <CopyField label="Caption" value={socialCaption.tiktok_caption} />
                <CopyField label="Hashtags" value={socialCaption.tiktok_hashtags} />
              </div>
            </div>
          )}

          <div className="flex gap-2 mt-2">
            <button onClick={onOpenPipelineModal} disabled={!!pipelineLoading} className="nb-btn nb-btn-primary flex-1" style={{ background: 'var(--yellow)', color: 'black', borderColor: 'black', boxShadow: '4px 4px 0px rgba(0,0,0,0.2)' }}>
              {pipelineLoading ? `🚀 ${pipelineLoading}` : '🚀 Full-Throttle Pipeline'}
            </button>
            <button onClick={handleOpenOutput} className="nb-btn nb-btn-ghost" title="Open output folder" style={{ minWidth: 40 }}>
              📂
            </button>
          </div>
        </div>

        {/* Middle: metadata + config */}
        <div className="nb-card p-4 flex flex-col gap-3">
          <div className="flex justify-between items-end mb-1">
            <div className="nb-label mb-0">MATERIAL STYLE</div>
            <button onClick={() => setShowMaterialModal(true)} className="nb-btn nb-btn-ghost text-[10px] px-2 py-1">
              Browse Library
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {project.material ? <Badge label={project.material} /> : <span className="text-[11px] italic" style={{ color: 'var(--muted)' }}>No style selected</span>}
          </div>

          <div className="nb-label mt-2 mb-1">CONFIG</div>
          <div className="flex flex-wrap gap-2 mb-1">
            {project.user_paygate_tier && (
              <span className="nb-badge" style={{ background: 'var(--text)', color: '#fff' }}>
                {project.user_paygate_tier.includes('TWO') ? 'TIER 2' : 'TIER 1'}
              </span>
            )}
            <Badge label={project.status} />
            {project.language && <Badge label={project.language} />}
          </div>
          
          <div className="flex flex-wrap gap-3 text-[11px] font-bold mt-1" style={{ color: 'var(--muted)' }}>
            <span>Created {formatDate(project.created_at)}</span>
            <span>Updated {formatDate(project.updated_at)}</span>
          </div>
          {project.narrator_voice && (
            <div className="text-[11px] font-bold" style={{ color: 'var(--muted)' }}>
              Narrator: <span className="font-black" style={{ color: 'var(--text)' }}>{project.narrator_voice}</span>
            </div>
          )}
          <div className="flex items-center gap-3 text-[11px] mt-1">
            {project.allow_music && (
              <span className="nb-badge" style={{ background: 'var(--text)', color: '#fff' }}>Music</span>
            )}
            {project.allow_voice && (
              <span className="nb-badge" style={{ background: 'var(--text)', color: '#fff' }}>Voice</span>
            )}
          </div>

          {/* Model selectors */}
          <div className="mt-2 flex flex-col gap-2">
            <div className="nb-label">MODELS</div>
            <div>
              <div className="text-[10px] font-black uppercase mb-1" style={{ color: 'var(--muted)' }}>Image</div>
              <div className="flex gap-2">
                <button onClick={() => selectModel('image', 'GEM_PIX_2')} disabled={modelLoading} className="text-[11px] font-black px-3 py-2 uppercase"
                  style={modelBtn(isImgGem)}>NANO BANANA PRO</button>
                <button onClick={() => selectModel('image', 'NARWHAL')} disabled={modelLoading} className="text-[11px] font-black px-3 py-2 uppercase"
                  style={modelBtn(isImgNar)}>NANO BANANA 2</button>
              </div>
            </div>
            <div>
              <div className="text-[10px] font-black uppercase mb-1" style={{ color: 'var(--muted)' }}>Upscale</div>
              <div className="flex gap-2">
                <button onClick={() => selectModel('upscale', 'veo_3_1_upsampler_1080p')} disabled={modelLoading} className="text-[11px] font-black px-3 py-2 uppercase"
                  style={modelBtn(isUp1080)}>1080p</button>
                <button onClick={() => selectModel('upscale', 'veo_3_1_upsampler_4k')} disabled={modelLoading} className="text-[11px] font-black px-3 py-2 uppercase"
                  style={modelBtn(isUp4k)}>4K</button>
              </div>
            </div>
            <div>
              <div className="text-[10px] font-black uppercase mb-1" style={{ color: 'var(--muted)' }}>Orientation</div>
              <div className="flex gap-2">
                <button onClick={() => patch('orientation', 'VERTICAL')} className="text-[11px] font-black px-3 py-2 uppercase"
                  style={modelBtn(project.orientation === 'VERTICAL')}>VERTICAL</button>
                <button onClick={() => patch('orientation', 'HORIZONTAL')} className="text-[11px] font-black px-3 py-2 uppercase"
                  style={modelBtn(project.orientation === 'HORIZONTAL')}>HORIZONTAL</button>
              </div>
            </div>
          </div>
        </div>

        {/* Right: config */}
        <div className="nb-card p-4 flex flex-col gap-3">
          {/* Detailed Config Options */}
          <div className="flex flex-col gap-4 h-full">
            <div className="nb-label">GENERATION CONFIG</div>
            
            <div className="flex flex-col gap-3 flex-1">
              <div className="flex flex-col gap-1">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--text)' }}>Assets (Characters)</span>
                  <div className="flex gap-1">
                    <button onClick={() => setConfig({ ...config, charMode: 'AUTO' })} className={`text-[9px] px-2 py-0.5 font-bold uppercase rounded-sm border-[1.5px] border-[var(--border)] ${config.charMode === 'AUTO' ? 'bg-[var(--text)] text-[var(--bg)]' : 'bg-[var(--bg)] text-[var(--text)]'}`}>Auto</button>
                    <button onClick={() => setConfig({ ...config, charMode: 'MANUAL' })} className={`text-[9px] px-2 py-0.5 font-bold uppercase rounded-sm border-[1.5px] border-[var(--border)] ${config.charMode !== 'AUTO' ? 'bg-[var(--text)] text-[var(--bg)]' : 'bg-[var(--bg)] text-[var(--text)]'}`}>Manual</button>
                  </div>
                </div>
                {config.charMode !== 'AUTO' && (
                  <div className="flex items-center gap-2">
                    <input type="number" min="0" max="20" className="nb-input w-full text-[12px] p-2" placeholder="Min" value={config.minChars} onChange={e => setConfig({ ...config, minChars: parseInt(e.target.value) || 0 })} />
                    <span className="text-[10px] font-black" style={{ color: 'var(--muted)' }}>TO</span>
                    <input type="number" min="0" max="20" className="nb-input w-full text-[12px] p-2" placeholder="Max" value={config.maxChars} onChange={e => setConfig({ ...config, maxChars: parseInt(e.target.value) || 0 })} />
                  </div>
                )}
              </div>
              <div className="flex flex-col gap-1">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--text)' }}>Assets (Locations)</span>
                  <div className="flex gap-1">
                    <button onClick={() => setConfig({ ...config, locMode: 'AUTO' })} className={`text-[9px] px-2 py-0.5 font-bold uppercase rounded-sm border-[1.5px] border-[var(--border)] ${config.locMode === 'AUTO' ? 'bg-[var(--text)] text-[var(--bg)]' : 'bg-[var(--bg)] text-[var(--text)]'}`}>Auto</button>
                    <button onClick={() => setConfig({ ...config, locMode: 'MANUAL' })} className={`text-[9px] px-2 py-0.5 font-bold uppercase rounded-sm border-[1.5px] border-[var(--border)] ${config.locMode !== 'AUTO' ? 'bg-[var(--text)] text-[var(--bg)]' : 'bg-[var(--bg)] text-[var(--text)]'}`}>Manual</button>
                  </div>
                </div>
                {config.locMode !== 'AUTO' && (
                  <div className="flex items-center gap-2">
                    <input type="number" min="0" max="20" className="nb-input w-full text-[12px] p-2" placeholder="Min" value={config.minLocs} onChange={e => setConfig({ ...config, minLocs: parseInt(e.target.value) || 0 })} />
                    <span className="text-[10px] font-black" style={{ color: 'var(--muted)' }}>TO</span>
                    <input type="number" min="0" max="20" className="nb-input w-full text-[12px] p-2" placeholder="Max" value={config.maxLocs} onChange={e => setConfig({ ...config, maxLocs: parseInt(e.target.value) || 0 })} />
                  </div>
                )}
              </div>
              <div className="flex flex-col gap-1">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--text)' }}>Assets (Props/Other)</span>
                  <div className="flex gap-1">
                    <button onClick={() => setConfig({ ...config, otherMode: 'AUTO' })} className={`text-[9px] px-2 py-0.5 font-bold uppercase rounded-sm border-[1.5px] border-[var(--border)] ${config.otherMode === 'AUTO' ? 'bg-[var(--text)] text-[var(--bg)]' : 'bg-[var(--bg)] text-[var(--text)]'}`}>Auto</button>
                    <button onClick={() => setConfig({ ...config, otherMode: 'MANUAL' })} className={`text-[9px] px-2 py-0.5 font-bold uppercase rounded-sm border-[1.5px] border-[var(--border)] ${config.otherMode !== 'AUTO' ? 'bg-[var(--text)] text-[var(--bg)]' : 'bg-[var(--bg)] text-[var(--text)]'}`}>Manual</button>
                  </div>
                </div>
                {config.otherMode !== 'AUTO' && (
                  <div className="flex items-center gap-2">
                    <input type="number" min="0" max="20" className="nb-input w-full text-[12px] p-2" placeholder="Min" value={config.minOthers} onChange={e => setConfig({ ...config, minOthers: parseInt(e.target.value) || 0 })} />
                    <span className="text-[10px] font-black" style={{ color: 'var(--muted)' }}>TO</span>
                    <input type="number" min="0" max="20" className="nb-input w-full text-[12px] p-2" placeholder="Max" value={config.maxOthers} onChange={e => setConfig({ ...config, maxOthers: parseInt(e.target.value) || 0 })} />
                  </div>
                )}
              </div>
              
              <div className="w-full h-px" style={{ background: 'var(--border)' }}></div>

              {/* TTS Template */}
              <div className="flex flex-col gap-1">
                <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--text)' }}>Narrator (TTS)</span>
                <select
                  className="nb-input w-full text-[11px] p-2"
                  value={config.ttsTemplate || ''}
                  onChange={e => setConfig({ ...config, ttsTemplate: e.target.value || null })}
                >
                  <option value="">— None —</option>
                  {ttsTemplates.map(t => (
                    <option key={t.name} value={t.name}>{t.name}</option>
                  ))}
                </select>
              </div>

              {/* Video Language */}
              <div className="flex flex-col gap-1">
                <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--text)' }}>Language</span>
                <select
                  className="nb-input w-full text-[11px] p-2"
                  value={config.videoLang || 'vi'}
                  onChange={e => setConfig({ ...config, videoLang: e.target.value })}
                >
                  {VIDEO_LANGUAGES.map(l => (
                    <option key={l.code} value={l.code}>{l.label}</option>
                  ))}
                </select>
              </div>

              <div className="w-full h-px" style={{ background: 'var(--border)' }}></div>

              <div className="flex flex-col gap-1">
                <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--text)' }}>Structure</span>
                <div className="flex items-center gap-2">
                  <div className="flex-1">
                    <span className="text-[9px] font-bold text-gray-500 block mb-1">Videos</span>
                    <input type="number" min="1" max="50" className="nb-input w-full text-[12px] p-2" value={config.videosCount} onChange={e => setConfig({ ...config, videosCount: parseInt(e.target.value) || 1 })} />
                  </div>
                  <span className="text-[10px] font-black mt-4" style={{ color: 'var(--muted)' }}>×</span>
                  <div className="flex-1">
                    <span className="text-[9px] font-bold text-gray-500 block mb-1">Scenes / Video</span>
                    <input type="number" min="1" max="50" className="nb-input w-full text-[12px] p-2" value={config.scenesPerVideo} onChange={e => setConfig({ ...config, scenesPerVideo: parseInt(e.target.value) || 1 })} />
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-auto p-3 rounded-md text-center shadow-[4px_4px_0px_rgba(0,0,0,1)]" style={{ background: 'var(--blue)', border: '2px solid black' }}>
              <div className="text-[12px] font-black uppercase text-white tracking-widest drop-shadow-md">
                Est. Duration: {config.videosCount * config.scenesPerVideo * 8}s
              </div>
              <div className="text-[10px] font-bold mt-1 text-blue-100 mix-blend-screen">
                {config.videosCount} videos × {config.scenesPerVideo} scenes × 8s
              </div>
            </div>
          </div>
        </div>
      </div>
      <MaterialBrowseModal
        open={showMaterialModal}
        onClose={() => setShowMaterialModal(false)}
        onSelect={(m) => {
          patch('material', m)
          setShowMaterialModal(false)
        }}
      />
    </>
  )
}
