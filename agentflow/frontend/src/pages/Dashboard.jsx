/**
 * Dashboard Page — execution stats, providers, tools
 */
import { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { getExecutions } from '../api/client';

export default function Dashboard() {
  const { health, tools, models } = useApp();
  const [stats, setStats] = useState(null);
  const [recentExecutions, setRecentExecutions] = useState([]);

  useEffect(() => {
    getExecutions()
      .then(d => {
        setStats(d.stats);
        setRecentExecutions(d.executions?.slice(0, 5) || []);
      })
      .catch(() => {});
  }, []);

  const StatCard = ({ title, value, sub, accent }) => (
    <div className="card" style={{position:'relative',overflow:'hidden'}}>
      <div className="card-title">{title}</div>
      <div className={`stat-value ${accent ? 'primary' : ''}`}>{value ?? '—'}</div>
      {sub && <div className="text-xs text-muted mt-2">{sub}</div>}
      <div style={{
        position:'absolute',right:-10,top:-10,
        fontSize:48,opacity:0.05,userSelect:'none',
        fontWeight:900,letterSpacing:-4,
      }}>{value ?? ''}</div>
    </div>
  );

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Real-time platform overview</p>
      </div>

      <div className="page-body">
        {/* Stats */}
        <div className="grid-cols-4" style={{marginBottom:24}}>
          <StatCard title="Total Executions" value={stats?.total} sub="All time" accent />
          <StatCard title="Completed" value={stats?.completed} sub="Successful" />
          <StatCard title="Failed" value={stats?.failed} sub="Error rate" />
          <StatCard
            title="Avg Latency"
            value={stats?.avg_latency_ms ? `${Math.round(stats.avg_latency_ms)}ms` : null}
            sub="Completed executions"
          />
        </div>

        <div className="grid-cols-2" style={{gap:16}}>
          {/* Providers */}
          <div className="card">
            <div className="card-title">LLM Providers</div>
            {models.map(p => (
              <div key={p.id} className="flex items-center justify-between" style={{padding:'8px 0',borderBottom:'1px solid var(--color-border)'}}>
                <div className="flex items-center gap-2">
                  <span className={`status-dot ${p.available ? 'ok' : 'warn'}`} />
                  <span style={{fontSize:14,fontWeight:500,textTransform:'capitalize'}}>{p.id}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`badge badge-${p.available ? 'success' : 'warning'}`}>
                    {p.available ? 'ready' : 'no key'}
                  </span>
                  <span className="text-xs text-muted">{p.models?.length || 0} models</span>
                </div>
              </div>
            ))}
          </div>

          {/* MCP Tools */}
          <div className="card">
            <div className="card-title">MCP Tools</div>
            <div style={{fontSize:12,color:'var(--color-text-muted)',marginBottom:10}}>
              Status: <span style={{color:'var(--color-success)'}}>●</span> {health?.mcp || 'unknown'}
            </div>
            {tools.map(t => (
              <div key={t.name} className="flex items-center justify-between" style={{padding:'8px 0',borderBottom:'1px solid var(--color-border)'}}>
                <div className="flex items-center gap-2">
                  <span className="tool-badge">🔧 {t.name}</span>
                </div>
                <span className="badge badge-success">available</span>
              </div>
            ))}
            {!tools.length && <div className="text-sm text-muted">Loading tools...</div>}
          </div>
        </div>

        {/* Recent Executions */}
        {recentExecutions.length > 0 && (
          <div className="card" style={{marginTop:16}}>
            <div className="card-title">Recent Executions</div>
            {recentExecutions.map(e => (
              <div key={e.id} className="flex items-center justify-between" style={{padding:'8px 0',borderBottom:'1px solid var(--color-border)'}}>
                <div>
                  <div style={{fontSize:13,fontFamily:'var(--font-mono)'}}>{e.id?.slice(0,8)}…</div>
                  <div className="text-xs text-muted">{new Date(e.created_at).toLocaleString()}</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`badge badge-${e.status === 'completed' ? 'success' : 'error'}`}>{e.status}</span>
                  {e.latency_ms && <span className="text-xs text-muted">{e.latency_ms}ms</span>}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* System health */}
        <div className="card" style={{marginTop:16}}>
          <div className="card-title">System Health</div>
          <div className="flex gap-4 flex-wrap">
            {[
              ['Backend', health?.status === 'ok', health?.status],
              ['Database', health?.database === 'connected', health?.database],
              ['MCP', health?.mcp === 'ready', health?.mcp],
              ['Version', true, `v${health?.version || '1.0.0'}`],
            ].map(([label, ok, val]) => (
              <div key={label} style={{fontSize:13}}>
                <span className={`status-dot ${ok ? 'ok' : 'warn'}`} />
                <span className="text-muted">{label}: </span>
                <span>{val ?? '...'}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
