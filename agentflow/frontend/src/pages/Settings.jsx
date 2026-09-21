/**
 * Settings Page — provider status, env config guidance
 */
import { useApp } from '../context/AppContext';

export default function Settings() {
  const { health, models, tools, refresh } = useApp();

  return (
    <div>
      <div className="page-header">
        <h1>Settings</h1>
        <p>Platform configuration and provider status</p>
      </div>
      <div className="page-body">
        <div style={{maxWidth:720,display:'flex',flexDirection:'column',gap:20}}>

          {/* Provider Status */}
          <div className="card">
            <div className="card-title">Provider Status</div>
            <div style={{fontSize:12,color:'var(--color-text-muted)',marginBottom:12}}>
              Providers are configured via environment variables on the backend. Never enter API keys in the frontend.
            </div>
            {models.map(p => (
              <div key={p.id} style={{padding:'12px 0',borderBottom:'1px solid var(--color-border)'}}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`status-dot ${p.available ? 'ok' : 'warn'}`} />
                    <span style={{fontSize:14,fontWeight:600,textTransform:'capitalize'}}>{p.id}</span>
                  </div>
                  <span className={`badge badge-${p.available ? 'success' : 'warning'}`}>
                    {p.available ? 'configured' : 'no API key'}
                  </span>
                </div>
                <div className="text-xs text-muted mt-2">
                  {p.id === 'gemini' && 'Set GEMINI_API_KEY in backend .env'}
                  {p.id === 'openrouter' && 'Set OPENROUTER_API_KEY in backend .env'}
                  {p.id === 'mock' && 'Always available — no credentials required'}
                </div>
                {p.models?.length > 0 && (
                  <div style={{display:'flex',gap:6,flexWrap:'wrap',marginTop:8}}>
                    {p.models.map(m => (
                      <span key={m.id} className={`badge badge-${m.free ? 'success' : 'secondary'}`}>
                        {m.name}{m.free ? ' ·free' : ''}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* MCP Tools */}
          <div className="card">
            <div className="card-title">MCP Tools</div>
            <div style={{fontSize:12,color:'var(--color-text-muted)',marginBottom:12}}>
              Tools are registered in the MCP server and discovered dynamically.
            </div>
            {tools.map(t => (
              <div key={t.name} style={{padding:'10px 0',borderBottom:'1px solid var(--color-border)'}}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="tool-badge">🔧 {t.name}</span>
                    <span className="badge badge-success">available</span>
                  </div>
                </div>
                <div className="text-xs text-muted mt-1">{t.description}</div>
              </div>
            ))}
          </div>

          {/* Health */}
          <div className="card">
            <div className="card-title">System Health</div>
            <div style={{display:'flex',flexDirection:'column',gap:8}}>
              {[
                ['Status', health?.status],
                ['Version', health?.version],
                ['Environment', health?.environment],
                ['Database', health?.database],
                ['MCP Server', health?.mcp],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between" style={{fontSize:13,padding:'4px 0',borderBottom:'1px solid var(--color-border)'}}>
                  <span className="text-muted">{k}</span>
                  <span style={{fontFamily:'var(--font-mono)'}}>{v || '...'}</span>
                </div>
              ))}
            </div>
            <button className="btn btn-secondary btn-sm mt-4" onClick={refresh}>↺ Refresh Status</button>
          </div>

          {/* Deployment */}
          <div className="card">
            <div className="card-title">Deployment</div>
            <div style={{fontSize:12,color:'var(--color-text-muted)',lineHeight:1.7}}>
              <div>• <b>Frontend:</b> Vercel — set <code style={{fontFamily:'var(--font-mono)',color:'var(--color-secondary)'}}>VITE_API_URL</code> to your Render backend URL</div>
              <div>• <b>Backend:</b> Render — set <code style={{fontFamily:'var(--font-mono)',color:'var(--color-secondary)'}}>DATABASE_URL</code>, <code style={{fontFamily:'var(--font-mono)',color:'var(--color-secondary)'}}>GEMINI_API_KEY</code>, <code style={{fontFamily:'var(--font-mono)',color:'var(--color-secondary)'}}>CORS_ORIGINS</code></div>
              <div>• <b>Database:</b> Supabase PostgreSQL — free tier</div>
              <div>• <b>Start command:</b> <code style={{fontFamily:'var(--font-mono)',color:'var(--color-secondary)'}}>uvicorn app.main:app --host 0.0.0.0 --port $PORT</code></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
