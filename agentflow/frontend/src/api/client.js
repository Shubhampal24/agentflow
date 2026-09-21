/**
 * AgentFlow API Client
 * All backend communication. Never exposes API keys.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data?.detail?.message || data?.message || `HTTP ${res.status}`);
    err.code = data?.detail?.code || 'UNKNOWN';
    err.status = res.status;
    throw err;
  }
  return data;
}

// ── Health ──────────────────────────────────────────────────────────────────
export const getHealth = () => request('/health');

// ── Models / Providers ──────────────────────────────────────────────────────
export const getModels = () => request('/api/models');
export const getProviders = () => request('/api/providers');

// ── Tools ───────────────────────────────────────────────────────────────────
export const getTools = () => request('/api/tools');

// ── Agents ──────────────────────────────────────────────────────────────────
export const getAgents = () => request('/api/agents');
export const getAgent = (id) => request(`/api/agents/${id}`);
export const createAgent = (body) => request('/api/agents', { method: 'POST', body: JSON.stringify(body) });
export const updateAgent = (id, body) => request(`/api/agents/${id}`, { method: 'PATCH', body: JSON.stringify(body) });

// ── Sessions ─────────────────────────────────────────────────────────────────
export const getSessions = () => request('/api/sessions');
export const getSession = (id) => request(`/api/sessions/${id}`);
export const createSession = (body) => request('/api/sessions', { method: 'POST', body: JSON.stringify(body) });
export const getSessionExecutions = (id) => request(`/api/sessions/${id}/executions`);

// ── Chat ─────────────────────────────────────────────────────────────────────
export const sendChat = (body) => request('/api/chat', { method: 'POST', body: JSON.stringify(body) });

// ── Executions ───────────────────────────────────────────────────────────────
export const getExecutions = () => request('/api/executions');
export const getExecution = (id) => request(`/api/executions/${id}`);
