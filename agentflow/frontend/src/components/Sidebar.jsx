/**
 * Sidebar navigation component
 */
import { useApp } from '../context/AppContext';

const NAV_ITEMS = [
  { id: 'dashboard',  label: 'Dashboard',   icon: '⬡' },
  { id: 'sessions',   label: 'Sessions',    icon: '💬' },
  { id: 'agents',     label: 'Agents',      icon: '🤖' },
  { id: 'executions', label: 'Executions',  icon: '⚡' },
  { id: 'settings',   label: 'Settings',    icon: '⚙️' },
];

function ProviderDot({ available }) {
  return <span className={`status-dot ${available ? 'ok' : 'warn'}`} />;
}

export default function Sidebar({ activePage, onNavigate }) {
  const { health, sidebarOpen, setSidebarOpen } = useApp();

  return (
    <>
      {/* Overlay on mobile */}
      {sidebarOpen && (
        <div
          style={{ position:'fixed',inset:0,background:'rgba(0,0,0,0.5)',zIndex:99 }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar${sidebarOpen ? ' open' : ''}`}>
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">⬡</div>
          <span className="sidebar-logo-text">AgentFlow</span>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              className={`nav-item${activePage === item.id ? ' active' : ''}`}
              onClick={() => { onNavigate(item.id); setSidebarOpen(false); }}
              title={item.label}
              aria-current={activePage === item.id ? 'page' : undefined}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        {/* System Status */}
        <div className="sidebar-footer">
          <div className="system-status">
            <div className="status-row">
              <span style={{fontWeight:600,color:'var(--color-text-secondary)',fontSize:11}}>System Status</span>
            </div>
            <div className="status-row">
              <span>
                <ProviderDot available={health?.database === 'connected'} />
                Database
              </span>
              <span>{health?.database ?? '...'}</span>
            </div>
            <div className="status-row">
              <span>
                <ProviderDot available={health?.mcp === 'ready'} />
                MCP
              </span>
              <span>{health?.mcp ?? '...'}</span>
            </div>
            <div className="status-row">
              <span>
                <ProviderDot available={health?.providers?.mock} />
                Mock
              </span>
              <span>{health?.providers?.mock ? 'ready' : 'N/A'}</span>
            </div>
            <div className="status-row">
              <span>
                <ProviderDot available={health?.providers?.gemini} />
                Gemini
              </span>
              <span>{health?.providers?.gemini ? 'ready' : 'no key'}</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
