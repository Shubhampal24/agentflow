/**
 * Executions Page — history, stats, execution detail
 */
import { useState, useEffect } from 'react';
import { getExecutions, getExecution } from '../api/client';
import ExecutionInspector from '../components/ExecutionInspector';

const STATUS_BADGE = {
  completed: 'badge-success',
  failed: 'badge-error',
  running: 'badge-warning',
};

const PROVIDER_BADGE = {
  mock: 'badge-mock',
  gemini: 'badge-gemini',
  openrouter: 'badge-openrouter',
};

export default function Executions() {
  const [executions, setExecutions] = useState([]);
  const [stats, setStats] = useState(null);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getExecutions()
      .then(d => { setExecutions(d.executions || []); setStats(d.stats); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function handleSelect(ex) {
    setSelected(ex);
  }

  return (
    <div style={{display:'flex',height:'100vh',overflow:'hidden'}}>
      <div style={{flex:1,display:'flex',flexDirection:'column',overflow:'hidden'}}>
        <div className="page-header">
          <h1>Executions</h1>
          <p>Complete history of all agent runs</p>
        </div>

        <div className="page-body" style={{overflowY:'auto'}}>
          {/* Stats bar */}
          {stats && (
            <div className="grid-cols-4" style={{marginBottom:20}}>
              {[
                ['Total', stats.total],
                ['Completed', stats.completed],
                ['Failed', stats.failed],
                ['Avg Latency', stats.avg_latency_ms ? `${Math.round(stats.avg_latency_ms)}ms` : '—'],
              ].map(([k, v]) => (
                <div key={k} className="card" style={{padding:'14px 16px'}}>
                  <div className="card-title">{k}</div>
                  <div className="stat-value" style={{fontSize:24}}>{v ?? '—'}</div>
                </div>
              ))}
            </div>
          )}

          {loading && (
            <div className="empty-state"><div className="spinner" /></div>
          )}

          {!loading && executions.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">⚡</div>
              <div className="empty-title">No executions yet</div>
              <div className="empty-desc">Run a chat in the Sessions page to see executions here.</div>
            </div>
          )}

          {executions.map(ex => (
            <div
              key={ex.id}
              className={`card${selected?.id === ex.id ? ' selected' : ''}`}
              style={{
                marginBottom:8,cursor:'pointer',
                border:selected?.id === ex.id ? '1px solid var(--color-primary)' : undefined,
              }}
              onClick={() => handleSelect(ex)}
              role="button"
              tabIndex={0}
              onKeyDown={e => e.key === 'Enter' && handleSelect(ex)}
            >
              <div className="flex items-center justify-between">
                <div style={{flex:1,minWidth:0}}>
                  <div className="flex items-center gap-2" style={{marginBottom:4}}>
                    <span className={`badge ${STATUS_BADGE[ex.status] || 'badge-secondary'}`}>{ex.status}</span>
                    <span className={`badge ${PROVIDER_BADGE[ex.provider] || 'badge-secondary'}`}>{ex.provider || '—'}</span>
                    {ex.fallback_used && <span className="badge badge-warning">⚡ fallback</span>}
                  </div>
                  <div style={{fontSize:13,color:'var(--color-text-secondary)',overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>
                    {ex.request || '—'}
                  </div>
                  <div className="text-xs text-muted mt-1">
                    {new Date(ex.created_at).toLocaleString()} · {ex.latency_ms ? `${ex.latency_ms}ms` : ''}
                  </div>
                </div>
                <div style={{fontSize:11,color:'var(--color-text-muted)',fontFamily:'var(--font-mono)',marginLeft:12}}>
                  {ex.id?.slice(0,8)}…
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Inspector */}
      <ExecutionInspector execution={selected} />
    </div>
  );
}
