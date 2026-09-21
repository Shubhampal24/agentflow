/**
 * Sessions Page — 3-column: sessions list / chat / execution inspector
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { useApp } from '../context/AppContext';
import ExecutionInspector from '../components/ExecutionInspector';
import ProviderSelector from '../components/ProviderSelector';
import {
  getSessions, createSession, getSessionExecutions, sendChat
} from '../api/client';

function MessageBubble({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`chat-message flex gap-2 ${isUser ? 'flex-row-reverse' : ''}`} style={{marginBottom:12}}>
      <div className={`message-avatar ${isUser ? 'message-avatar-user' : 'message-avatar-assistant'}`}>
        {isUser ? '👤' : '⬡'}
      </div>
      <div className={`message-${isUser ? 'user' : 'assistant'}`}>
        <div className="message-bubble">{msg.content}</div>
        {msg.tools_used?.length > 0 && (
          <div className="flex gap-1 mt-2 flex-wrap">
            {msg.tools_used.map(t => (
              <span key={t.name} className="tool-badge" style={{fontSize:10}}>
                🔧 {t.name} · {t.duration_ms}ms
              </span>
            ))}
          </div>
        )}
        {msg.provider && (
          <div className="text-xs text-muted mt-1" style={{textAlign: isUser ? 'right' : 'left'}}>
            {msg.provider} · {msg.latency_ms}ms
            {msg.fallback_used && ' · ⚡ fallback'}
          </div>
        )}
      </div>
    </div>
  );
}

export default function Sessions() {
  const { selectedProvider, selectedModel } = useApp();

  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastExecution, setLastExecution] = useState(null);

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  const loadSessions = useCallback(async () => {
    try {
      const d = await getSessions();
      setSessions(d.sessions || []);
    } catch {}
  }, []);

  useEffect(() => { loadSessions(); }, [loadSessions]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function handleNewSession() {
    try {
      const s = await createSession({ title: 'New Session' });
      setSessions(prev => [s, ...prev]);
      setActiveSessionId(s.id);
      setMessages([]);
      setLastExecution(null);
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleSelectSession(id) {
    setActiveSessionId(id);
    setMessages([]);
    setLastExecution(null);
    try {
      const execs = await getSessionExecutions(id);
      const recent = (execs.executions || []).slice(0, 10).reverse();
      const msgs = [];
      for (const ex of recent) {
        if (ex.request) msgs.push({ role: 'user', content: ex.request });
        if (ex.response) msgs.push({
          role: 'assistant',
          content: ex.response,
          provider: ex.provider,
          latency_ms: ex.latency_ms,
          fallback_used: ex.fallback_used,
          tools_used: [],
        });
      }
      setMessages(msgs);
    } catch {}
  }

  async function handleSend() {
    if (!input.trim() || loading || !activeSessionId) return;
    const userMsg = input.trim();
    setInput('');
    setError('');

    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const result = await sendChat({
        session_id: activeSessionId,
        message: userMsg,
        provider: selectedProvider,
        model: selectedModel,
      });

      if (result.success) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: result.response,
          provider: result.provider,
          model: result.model,
          latency_ms: result.latency_ms,
          fallback_used: result.fallback_used,
          tools_used: result.tools_used || [],
        }]);
        setLastExecution(result);
      } else {
        const code = result.error?.code || result.error_code || 'AGENT_ERROR';
        const friendlyMsg = {
          LLM_RATE_LIMIT: 'Selected model is temporarily rate limited.',
          PROVIDER_UNAVAILABLE: 'Provider unavailable.',
          MCP_TOOL_ERROR: 'The requested tool could not be executed.',
          LLM_AUTH_ERROR: 'Provider authentication failed. Check API key.',
        }[code] || result.error?.message || 'Agent encountered an error.';
        setError(`${code}: ${friendlyMsg}`);
        setLastExecution(result);
      }
    } catch (e) {
      setError(e.message || 'Failed to send message.');
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  }

  const SUGGESTIONS = [
    'Calculate 12345 * 678',
    'What time is it in Asia/Kolkata?',
    'Count words in: The quick brown fox jumps over the lazy dog',
    'Explain what LangGraph is',
  ];

  return (
    <div style={{display:'flex',height:'100vh',overflow:'hidden'}}>
      {/* Sessions list */}
      <div style={{
        width:220,background:'var(--color-surface)',
        borderRight:'1px solid var(--color-border)',
        display:'flex',flexDirection:'column',flexShrink:0,
      }}>
        <div style={{padding:'16px',borderBottom:'1px solid var(--color-border)'}}>
          <button className="btn btn-primary w-full btn-sm" onClick={handleNewSession} id="new-session-btn">
            + New Session
          </button>
        </div>
        <div style={{flex:1,overflowY:'auto',padding:'8px'}}>
          {sessions.length === 0 && (
            <div className="empty-state" style={{padding:24}}>
              <div className="empty-desc">No sessions yet. Create one!</div>
            </div>
          )}
          {sessions.map(s => (
            <div
              key={s.id}
              className={`session-item${activeSessionId === s.id ? ' active' : ''}`}
              onClick={() => handleSelectSession(s.id)}
              role="button"
              tabIndex={0}
              onKeyDown={e => e.key === 'Enter' && handleSelectSession(s.id)}
            >
              <div className="session-title">{s.title || 'Untitled Session'}</div>
              <div className="session-meta">{new Date(s.created_at).toLocaleDateString()}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div style={{flex:1,display:'flex',flexDirection:'column',overflow:'hidden'}}>
        {/* Provider bar */}
        <div style={{
          padding:'10px 16px',
          borderBottom:'1px solid var(--color-border)',
          background:'var(--color-surface)',
          display:'flex',alignItems:'center',gap:12,flexWrap:'wrap',
        }}>
          <ProviderSelector compact />
        </div>

        {/* Messages */}
        <div style={{flex:1,overflowY:'auto',padding:'20px 24px'}}>
          {!activeSessionId ? (
            <div className="empty-state">
              <div className="empty-icon">💬</div>
              <div className="empty-title">Start a session</div>
              <div className="empty-desc">Create a new session or select an existing one to begin chatting.</div>
              <button className="btn btn-primary mt-4" onClick={handleNewSession}>New Session</button>
            </div>
          ) : messages.length === 0 && !loading ? (
            <div className="empty-state">
              <div className="empty-icon">⬡</div>
              <div className="empty-title">AgentFlow is ready</div>
              <div className="empty-desc">Try a calculation, time zone lookup, text analysis, or ask anything.</div>
              <div style={{display:'flex',flexDirection:'column',gap:8,marginTop:16,width:'100%',maxWidth:360}}>
                {SUGGESTIONS.map(s => (
                  <button
                    key={s}
                    className="btn btn-secondary"
                    style={{textAlign:'left',fontSize:12}}
                    onClick={() => { setInput(s); inputRef.current?.focus(); }}
                  >{s}</button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((m, i) => <MessageBubble key={i} msg={m} />)}
              {loading && (
                <div className="flex items-center gap-2" style={{padding:'8px 0',color:'var(--color-text-muted)'}}>
                  <div className="spinner" style={{width:16,height:16}} />
                  <span style={{fontSize:13}}>Agent is working...</span>
                </div>
              )}
              {error && (
                <div className="error-card" style={{margin:'8px 0'}}>
                  <div className="error-card-icon">⚠</div>
                  <div className="error-card-content">
                    <div className="error-card-title">Error</div>
                    <div className="error-card-msg">{error}</div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </>
          )}
        </div>

        {/* Composer */}
        <div style={{
          padding:'12px 16px',
          borderTop:'1px solid var(--color-border)',
          background:'var(--color-surface)',
        }}>
          <div className="flex gap-2">
            <textarea
              ref={inputRef}
              className="textarea"
              style={{minHeight:44,maxHeight:120,resize:'none'}}
              placeholder={activeSessionId ? 'Type a message… (Enter to send, Shift+Enter for newline)' : 'Create a session first'}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={!activeSessionId || loading}
              aria-label="Chat message input"
              id="chat-input"
            />
            <button
              className="btn btn-primary"
              style={{alignSelf:'flex-end',padding:'10px 18px'}}
              onClick={handleSend}
              disabled={!input.trim() || loading || !activeSessionId}
              id="send-btn"
              aria-label="Send message"
            >
              {loading ? <div className="spinner" style={{width:16,height:16,borderTopColor:'#fff'}} /> : '↑'}
            </button>
          </div>
        </div>
      </div>

      {/* Inspector */}
      <ExecutionInspector execution={lastExecution} />
    </div>
  );
}
