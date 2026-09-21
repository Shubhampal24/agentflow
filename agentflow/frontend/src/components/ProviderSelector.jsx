/**
 * Provider and Model selector component
 */
import { useApp } from '../context/AppContext';

const PROVIDER_ICONS = {
  gemini: '✦',
  openrouter: '🔀',
  mock: '⚗️',
};

const PROVIDER_BADGE_CLASS = {
  gemini: 'badge-gemini',
  openrouter: 'badge-openrouter',
  mock: 'badge-mock',
};

export default function ProviderSelector({ compact = false }) {
  const {
    models: providerList,
    selectedProvider, setSelectedProvider,
    selectedModel, setSelectedModel,
    isProviderAvailable, getModelsForProvider,
  } = useApp();

  const availableModels = getModelsForProvider(selectedProvider);

  function handleProviderChange(pid) {
    if (!isProviderAvailable(pid)) return;
    setSelectedProvider(pid);
    const pModels = getModelsForProvider(pid);
    setSelectedModel(pModels[0]?.id || '');
  }

  if (compact) {
    return (
      <div className="flex gap-2 items-center flex-wrap">
        {providerList.map(p => (
          <button
            key={p.id}
            className={`provider-pill${selectedProvider === p.id ? ' selected' : ''}${!p.available ? ' disabled' : ''}`}
            onClick={() => handleProviderChange(p.id)}
            title={!p.available ? `${p.id} — no API key configured` : p.id}
            disabled={!p.available}
            aria-pressed={selectedProvider === p.id}
          >
            <span>{PROVIDER_ICONS[p.id] || '○'}</span>
            {p.id}
            {!p.available && <span style={{opacity:0.5}}>⚠</span>}
          </button>
        ))}
        {availableModels.length > 1 && (
          <select
            className="select"
            style={{height:32,fontSize:12,padding:'4px 28px 4px 8px',width:'auto'}}
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
            aria-label="Select model"
          >
            {availableModels.map(m => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        )}
      </div>
    );
  }

  return (
    <div style={{display:'flex',flexDirection:'column',gap:16}}>
      <div>
        <div className="form-label" style={{marginBottom:8}}>Provider</div>
        <div className="flex gap-2 flex-wrap">
          {providerList.map(p => (
            <button
              key={p.id}
              className={`provider-pill${selectedProvider === p.id ? ' selected' : ''}${!p.available ? ' disabled' : ''}`}
              onClick={() => handleProviderChange(p.id)}
              title={!p.available ? `${p.id} — API key not configured` : ''}
              disabled={!p.available}
            >
              <span>{PROVIDER_ICONS[p.id] || '○'}</span>
              {p.id.charAt(0).toUpperCase() + p.id.slice(1)}
              {!p.available && <span style={{opacity:0.5,fontSize:10}}> (no key)</span>}
            </button>
          ))}
        </div>
      </div>
      {availableModels.length > 0 && (
        <div className="form-group">
          <label className="form-label" htmlFor="model-select">Model</label>
          <select
            id="model-select"
            className="select"
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
          >
            {availableModels.map(m => (
              <option key={m.id} value={m.id}>
                {m.name}{m.free ? ' (Free)' : ''}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}
