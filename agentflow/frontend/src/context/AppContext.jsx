/**
 * AgentFlow — App Context
 * Global state: health, providers, tools, active session
 */
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getHealth, getModels, getTools } from '../api/client';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [health, setHealth] = useState(null);
  const [models, setModels] = useState([]);
  const [tools, setTools] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [selectedProvider, setSelectedProvider] = useState('mock');
  const [selectedModel, setSelectedModel] = useState('mock-model');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const [h, m, t] = await Promise.allSettled([
        getHealth(), getModels(), getTools()
      ]);
      if (h.status === 'fulfilled') setHealth(h.value);
      if (m.status === 'fulfilled') {
        const providers = m.value.providers || [];
        setModels(providers);
        // Auto-select first available provider
        const mockProvider = providers.find(p => p.id === 'mock');
        if (mockProvider) {
          setSelectedProvider('mock');
          setSelectedModel('mock-model');
        }
      }
      if (t.status === 'fulfilled') setTools(t.value.tools || []);
    } catch (e) {
      console.error('App init error:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const getModelsForProvider = (providerId) => {
    const p = models.find(p => p.id === providerId);
    return p?.models || [];
  };

  const isProviderAvailable = (providerId) => {
    const p = models.find(p => p.id === providerId);
    return p?.available ?? false;
  };

  return (
    <AppContext.Provider value={{
      health, models, tools,
      activeSession, setActiveSession,
      selectedProvider, setSelectedProvider,
      selectedModel, setSelectedModel,
      sidebarOpen, setSidebarOpen,
      loading, refresh,
      getModelsForProvider, isProviderAvailable,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export const useApp = () => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be inside AppProvider');
  return ctx;
};
