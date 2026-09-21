import { useState } from 'react';
import { AppProvider } from './context/AppContext';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Sessions from './pages/Sessions';
import Agents from './pages/Agents';
import Executions from './pages/Executions';
import Settings from './pages/Settings';
import './index.css';

const PAGES = {
  dashboard: Dashboard,
  sessions: Sessions,
  agents: Agents,
  executions: Executions,
  settings: Settings,
};

function MobileHeader({ onMenuClick }) {
  return (
    <header className="mobile-header">
      <button className="hamburger" onClick={onMenuClick} aria-label="Open navigation menu">☰</button>
      <div style={{display:'flex',alignItems:'center',gap:8}}>
        <div style={{
          width:24,height:24,background:'linear-gradient(135deg,var(--color-primary),var(--color-accent))',
          borderRadius:'var(--radius-sm)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:12,
        }}>⬡</div>
        <span style={{fontWeight:700,fontSize:16,letterSpacing:'-0.02em'}}>AgentFlow</span>
      </div>
    </header>
  );
}

function AppInner() {
  const [activePage, setActivePage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const PageComponent = PAGES[activePage] || Dashboard;
  const isFullPage = activePage === 'sessions' || activePage === 'executions';

  return (
    <div className="app-layout">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      <div className="main-content">
        <MobileHeader onMenuClick={() => setSidebarOpen(s => !s)} />
        <main style={{flex:1,display:'flex',flexDirection:'column',overflow:isFullPage ? 'hidden' : 'auto'}}>
          <PageComponent />
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppInner />
    </AppProvider>
  );
}
