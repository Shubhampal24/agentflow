/**
 * Agents Page — create, list, and configure agents
 */
import { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import ProviderSelector from '../components/ProviderSelector';
import { getAgents, createAgent } from '../api/client';

const DEFAULT_FORM = {
  name: '', description: '', system_prompt: '',
  provider: 'mock', model: 'mock-model',
};

export default function Agents() {
  const { models } = useApp();
  const [agents, setAgents] = useState([]);
  const [form, setForm] = useState(DEFAULT_FORM);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    getAgents().then(d => setAgents(d.agents || [])).catch(() => {});
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    if (!form.name.trim()) { setError('Agent name is required.'); return; }
    setCreating(true); setError(''); setSuccess('');
    try {
      const agent = await createAgent(form);
      setAgents(prev => [agent, ...prev]);
      setForm(DEFAULT_FORM);
      setSuccess('Agent created successfully!');
    } catch (e) {
      setError(e.message || 'Failed to create agent.');
    } finally {
      setCreating(false);
    }
  }

  const getModelsForProvider = (pid) => {
    const p = models.find(m => m.id === pid);
    return p?.models || [];
  };

  return (
    <div>
      <div className="page-header">
        <h1>Agents</h1>
        <p>Configure AI agents with custom providers and system prompts</p>
      </div>
      <div className="page-body">
        <div className="grid-cols-2" style={{gap:24,alignItems:'start'}}>
          {/* Create form */}
          <div className="card">
            <div className="card-title">Create Agent</div>
            <form onSubmit={handleCreate} style={{display:'flex',flexDirection:'column',gap:14,marginTop:8}}>
              <div className="form-group">
                <label className="form-label" htmlFor="agent-name">Name *</label>
                <input
                  id="agent-name"
                  className="input"
                  placeholder="e.g. Research Assistant"
                  value={form.name}
                  onChange={e => setForm(f => ({...f, name: e.target.value}))}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="agent-desc">Description</label>
                <input
                  id="agent-desc"
                  className="input"
                  placeholder="What does this agent do?"
                  value={form.description}
                  onChange={e => setForm(f => ({...f, description: e.target.value}))}
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="agent-provider">Provider</label>
                <select
                  id="agent-provider"
                  className="select"
                  value={form.provider}
                  onChange={e => {
                    const pid = e.target.value;
                    const ms = getModelsForProvider(pid);
                    setForm(f => ({...f, provider: pid, model: ms[0]?.id || ''}));
                  }}
                >
                  {models.map(p => (
                    <option key={p.id} value={p.id} disabled={!p.available}>
                      {p.id}{!p.available ? ' (no key)' : ''}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="agent-model">Model</label>
                <select
                  id="agent-model"
                  className="select"
                  value={form.model}
                  onChange={e => setForm(f => ({...f, model: e.target.value}))}
                >
                  {getModelsForProvider(form.provider).map(m => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="agent-prompt">System Prompt</label>
                <textarea
                  id="agent-prompt"
                  className="textarea"
                  placeholder="You are a helpful AI assistant..."
                  value={form.system_prompt}
                  onChange={e => setForm(f => ({...f, system_prompt: e.target.value}))}
                />
              </div>
              {error && <div className="error-card"><div className="error-card-content"><div className="error-card-title">{error}</div></div></div>}
              {success && <div style={{color:'var(--color-success)',fontSize:13}}>{success}</div>}
              <button type="submit" className="btn btn-primary" disabled={creating} id="create-agent-btn">
                {creating ? 'Creating…' : 'Create Agent'}
              </button>
            </form>
          </div>

          {/* Agent list */}
          <div>
            <div className="card-title" style={{marginBottom:12}}>Existing Agents ({agents.length})</div>
            {agents.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">🤖</div>
                <div className="empty-title">No agents yet</div>
                <div className="empty-desc">Create your first agent using the form on the left.</div>
              </div>
            )}
            {agents.map(a => (
              <div key={a.id} className="card" style={{marginBottom:12}}>
                <div className="flex items-center justify-between mb-2">
                  <div style={{fontSize:15,fontWeight:600}}>{a.name}</div>
                  <span className={`badge badge-${a.provider === 'mock' ? 'mock' : a.provider === 'gemini' ? 'gemini' : 'openrouter'}`}>
                    {a.provider}
                  </span>
                </div>
                {a.description && <div className="text-sm text-muted mb-2">{a.description}</div>}
                <div className="text-xs text-muted font-mono">{a.model}</div>
                {a.system_prompt && (
                  <div style={{
                    marginTop:8,padding:'8px',background:'var(--color-surface-2)',
                    borderRadius:'var(--radius-sm)',fontSize:11,color:'var(--color-text-muted)',
                    fontFamily:'var(--font-mono)',maxHeight:48,overflow:'hidden',textOverflow:'ellipsis',
                  }}>
                    {a.system_prompt}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
