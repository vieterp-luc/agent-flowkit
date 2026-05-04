import { BrowserRouter, NavLink, Routes, Route, useLocation } from 'react-router-dom'
import { LayoutDashboard, FolderOpen, ScrollText, Film, Star, Zap } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useWebSocket } from './api/useWebSocket'
import { fetchAPI } from './api/client'
import DashboardPage from './pages/DashboardPage'
import ProjectsPage from './pages/ProjectsPage'
import LogsPage from './pages/LogsPage'
import GalleryPage from './pages/GalleryPage'
import LibraryPage from './pages/LibraryPage'

type NavItem = { to: string; icon: React.ComponentType<{ size: number }>; label: string; exact: boolean }

const NAV: NavItem[] = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', exact: true },
  { to: '/projects', icon: FolderOpen, label: 'Projects', exact: false },
  { to: '/gallery', icon: Film, label: 'Gallery', exact: false },
  { to: '/library', icon: ScrollText, label: 'Library', exact: false },
  { to: '/logs', icon: ScrollText, label: 'Logs', exact: false },
]

function PageTitle() {
  const loc = useLocation()
  const match = NAV.find(n => n.exact ? loc.pathname === n.to : loc.pathname.startsWith(n.to))
  return <span className="font-black tracking-wider uppercase text-sm">{match?.label ?? 'Dashboard'}</span>
}

function Layout() {
  const { isConnected } = useWebSocket()
  const [activeProjectName, setActiveProjectName] = useState<string | null>(null)
  const [credits, setCredits] = useState<{ credits: number; tier: string } | null>(null)

  useEffect(() => {
    fetchAPI<{ project_id: string } | null>('/api/active-project')
      .then(active => {
        if (active?.project_id) {
          fetchAPI<{ name: string }>(`/api/projects/${active.project_id}`)
            .then(p => setActiveProjectName(p.name))
            .catch(() => setActiveProjectName(null))
        } else {
          setActiveProjectName(null)
        }
      })
      .catch(() => setActiveProjectName(null))
  }, [])

  useEffect(() => {
    fetchAPI<{ credits: number; tier: string }>('/api/flow/credits')
      .then(setCredits)
      .catch(() => setCredits(null))
  }, [])

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg)', color: 'var(--text)' }}>
      {/* Left sidebar — solid black border right */}
      <aside
        className="w-52 flex-shrink-0 flex flex-col"
        style={{ background: 'var(--surface)', borderRight: '3px solid var(--border)' }}
      >
        {/* Logo / Brand */}
        <div
          className="px-5 py-5 font-black text-base tracking-widest uppercase border-b"
          style={{ borderColor: 'var(--border)', color: 'var(--text)' }}
        >
          Flow Agent
        </div>

        <nav className="flex flex-col gap-1 px-3 py-4">
          {NAV.map(({ to, icon: Icon, label, exact }) => (
            <NavLink
              key={to}
              to={to}
              end={exact}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2.5 text-xs font-bold uppercase tracking-wide transition-all duration-150 ${
                  isActive ? '' : 'opacity-60'
                }`
              }
              style={({ isActive }) => ({
                background: isActive ? 'var(--text)' : 'transparent',
                color: isActive ? '#fff' : 'var(--text)',
                border: isActive ? '2px solid var(--border)' : '2px solid transparent',
                boxShadow: isActive ? 'var(--shadow-sm)' : 'none',
              })}
            >
              <Icon size={14} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Active project indicator */}
        {activeProjectName && (
          <div
            className="mt-auto px-4 py-4 border-t"
            style={{ borderColor: 'var(--border)' }}
          >
            <div
              className="flex items-center gap-1.5 mb-2 text-[10px] font-black uppercase tracking-widest"
              style={{ color: 'var(--muted)' }}
            >
              <Star size={9} />
              Active
            </div>
            <div
              className="text-xs font-bold truncate mono"
              style={{ color: 'var(--text)' }}
              title={activeProjectName}
            >
              {activeProjectName}
            </div>
          </div>
        )}
      </aside>

      {/* Main area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top header */}
        <header
          className="flex items-center justify-between px-6 py-4 border-b flex-shrink-0"
          style={{ background: 'var(--bg)', borderColor: 'var(--border)', borderBottomWidth: '2px' }}
        >
          <span className="text-sm font-bold tracking-wider" style={{ color: 'var(--text)' }}>
            <PageTitle />
          </span>
          <div className="flex items-center gap-4 text-xs font-semibold" style={{ color: 'var(--muted)' }}>
            {credits && (
              <span className="flex items-center gap-1.5">
                <Zap size={12} />
                <span style={{ color: (credits.tier ?? '').includes('TWO') ? 'var(--text)' : 'var(--muted)' }}>
                  {credits.credits.toLocaleString()} {credits.tier}
                </span>
              </span>
            )}
            <span className="flex items-center gap-1.5">
              <span
                className="inline-block w-2 h-2"
                style={{
                  background: isConnected ? 'var(--green)' : 'var(--red)',
                  border: '1.5px solid var(--border)',
                }}
              />
              {isConnected ? 'WS OK' : 'WS OFF'}
            </span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/projects/:id" element={<ProjectsPage />} />
            <Route path="/logs" element={<LogsPage />} />
            <Route path="/gallery" element={<GalleryPage />} />
            <Route path="/library" element={<LibraryPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  )
}
