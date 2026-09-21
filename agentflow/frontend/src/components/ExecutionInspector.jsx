/**
 * Execution Inspector — shows trace, tools, metadata for an execution
 */
import { useState } from 'react';

const EVENT_COLORS = {
  request_received:   'var(--color-info)',
  agent_started:      'var(--color-primary)',
  request_analyzed:   'var(--color-secondary)',
  tool_selected:      'var(--color-warning)',
  mcp_tool_started:   'var(--color-warning)',
  mcp_tool_completed: 'var(--color-success)',
  mcp_tool_failed:    'var(--color-error)',
  llm_started:        'var(--color-primary)',
  llm_completed:      'var(--color-success)',
  fallback_triggered: 'var(--color-warning)',
  execution_completed:'var(--color-success)',
  execution_failed:   'var(--color-error)',
};

function TraceTimeline({ trace = [] }) {
  if (!trace.length) return (
    <div className="empty-state" style={{padding:'24px'}}>
      <div className="empty-icon">⏱</div>
      <div className="empty-desc">No trace events yet</div>
    </div>
  );
  return (
    <div>
      {trace.map((evt, i) => (
        <div key={i} className="trace-item">
          <div className="trace-dot" style={{background: EVENT_COLORS[evt.event] || '#666'}} />
          <div style={{flex:1,minWidth:0}}>
            <div className="trace-event">{evt.event}</div>
            {evt.detail && <div className="trace-detail">{evt.detail}</div>}
          </div>
          <div className="trace-time">
            {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : ''}
          </div>
        </div>
      ))}
    </div>
  );
}

function ToolsPanel({ toolsUsed = [] }) {
  if (!toolsUsed.length) return (
    <div className="empty-state" style={{padding:'24px'}}>
      <div className="empty-icon">🔧</div>
      <div className="empty-desc">No MCP tools were used in this execution</div>
    </div>
  );
  return (
    <div style={{display:'flex',flexDirection:'column',gap:12}}>
      {toolsUsed.map((t, i) => (
        <div key={i} className="card" style={{padding:14}}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="tool-badge">🔧 {t.name}</span>
              <span className={`badge badge-${t.status === 'completed' ? 'success' : 'error'}`}>
                {t.status}
              </span>
            </div>
            <span className="text-xs text-muted">{t.duration_ms}ms</span>
          </div>
          {t.result && (
            <pre style={{
              fontSize:11,fontFamily:'var(--font-mono)',
              background:'var(--color-surface-3)',
              borderRadius:'var(--radius-sm)',
              padding:'8px',
              overflowX:'auto',
              color:'var(--color-secondary)',
            }}>
              {JSON.stringify(t.result, null, 2)}
            </pre>
          )}
        </div>
      ))}
    </div>
  );
}

function MetadataPanel({ execution }) {
  if (!execution) return (
    <div className="empty-state" style={{padding:'24px'}}>
      <div className="empty-desc">Run a chat message to see metadata</div>
    </div>
  );
  const rows = [
    ['Request ID', execution.request_id],
    ['Execution ID', execution.execution_id],
    ['Session ID', execution.session_id],
    ['Provider', execution.provider],
    ['Model', execution.model],
    ['Requested Provider', execution.requested_provider],
    ['Fallback Used', execution.fallback_used ? `Yes — ${execution.fallback_reason}` : 'No'],
    ['Latency', execution.latency_ms ? `${execution.latency_ms}ms` : '—'],
    ['Status', execution.status],
  ];
  return (
    <div style={{display:'flex',flexDirection:'column',gap:6}}>
      {rows.map(([k, v]) => v && (
        <div key={k} className="flex justify-between" style={{fontSize:12,padding:'6px 0',borderBottom:'1px solid var(--color-border)'}}>
          <span className="text-muted">{k}</span>
          <span style={{fontFamily:'var(--font-mono)',color:'var(--color-text-primary)',textAlign:'right',maxWidth:160,overflow:'hidden',textOverflow:'ellipsis'}}>{String(v)}</span>
        </div>
      ))}
    </div>
  );
}

function OverviewPanel({ execution }) {
  if (!execution) return (
    <div className="empty-state" style={{padding:'24px'}}>
      <div className="empty-icon">📊</div>
      <div className="empty-desc">Run a chat to see execution overview</div>
    </div>
  );

  const statusBadge = execution.status === 'completed' ? 'badge-success'
    : execution.status === 'failed' ? 'badge-error' : 'badge-warning';

  const providerBadge = {
    mock: 'badge-mock', gemini: 'badge-gemini', openrouter: 'badge-openrouter',
  }[execution.provider] || 'badge-secondary';

  return (
    <div style={{display:'flex',flexDirection:'column',gap:12}}>
      <div className="card" style={{padding:14}}>
        <div className="card-title">Status</div>
        <span className={`badge ${statusBadge}`}>{execution.status}</span>
        {execution.fallback_used && (
          <div style={{marginTop:8}}>
            <span className="badge badge-warning">⚡ Fallback Used</span>
            <div className="text-xs text-muted mt-2">{execution.fallback_reason}</div>
          </div>
        )}
      </div>
      <div className="card" style={{padding:14}}>
        <div className="card-title">Provider</div>
        <span className={`badge ${providerBadge}`}>{execution.provider || '—'}</span>
        {execution.requested_provider && execution.requested_provider !== execution.provider && (
          <div className="text-xs text-muted mt-2">Requested: {execution.requested_provider}</div>
        )}
        {execution.model && <div className="text-xs text-muted mt-1">{execution.model}</div>}
      </div>
      <div className="card" style={{padding:14}}>
        <div className="card-title">Latency</div>
        <div style={{fontSize:24,fontWeight:700,color:'var(--color-primary-h)'}}>
          {execution.latency_ms ? `${execution.latency_ms}ms` : '—'}
        </div>
      </div>
    </div>
  );
}

export default function ExecutionInspector({ execution }) {
  const [tab, setTab] = useState('overview');

  const TABS = [
    { id: 'overview', label: 'Overview' },
    { id: 'trace',    label: 'Trace' },
    { id: 'tools',    label: 'Tools' },
    { id: 'meta',     label: 'Metadata' },
  ];

  return (
    <aside className="inspector">
      <div style={{padding:'12px 16px',borderBottom:'1px solid var(--color-border)'}}>
        <div style={{fontSize:12,fontWeight:600,color:'var(--color-text-secondary)'}}>
          Execution Inspector
        </div>
      </div>
      <div className="inspector-tabs">
        {TABS.map(t => (
          <button
            key={t.id}
            className={`inspector-tab${tab === t.id ? ' active' : ''}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="inspector-body">
        {tab === 'overview' && <OverviewPanel execution={execution} />}
        {tab === 'trace' && <TraceTimeline trace={execution?.trace} />}
        {tab === 'tools' && <ToolsPanel toolsUsed={execution?.tools_used} />}
        {tab === 'meta' && <MetadataPanel execution={execution} />}
      </div>
    </aside>
  );
}
