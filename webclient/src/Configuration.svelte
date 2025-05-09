<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade } from 'svelte/transition';
  import { appState } from './lib/websocket.js';
  
  // State for settings data
  let settingsData = {};
  let isLoading = true;
  let error = null;
  let successMessage = '';
  
  // Track settings that have been modified but not saved
  let modifiedSettings = {};
  
  // Settings schema - provides metadata for each setting
  const settingsSchema = {
    'core.CPU_USAGE': {
      type: 'number', 
      label: 'CPU Usage', 
      description: 'Number of CPU cores to allocate to Renardo processes',
      group: 'Performance',
      min: 1,
      max: 16
    },
    'core.CLOCK_LATENCY': { 
      type: 'number', 
      label: 'Clock Latency', 
      description: 'Latency adjustment for timing in milliseconds',
      group: 'Performance',
      min: 0,
      max: 500
    },
    'core.COLLECTIONS_DOWNLOAD_SERVER': { 
      type: 'string', 
      label: 'Collections Server', 
      description: 'URL for the collections download server',
      group: 'Network'
    },
    'sc_backend.PORT': { 
      type: 'number', 
      label: 'SuperCollider Port', 
      description: 'Network port for SuperCollider communication',
      group: 'SuperCollider',
      min: 1024,
      max: 65535
    },
    'sc_backend.PORT2': { 
      type: 'number', 
      label: 'SuperCollider Secondary Port', 
      description: 'Secondary network port for SuperCollider',
      group: 'SuperCollider',
      min: 1024,
      max: 65535
    },
    'sc_backend.FORWARD_PORT': { 
      type: 'number', 
      label: 'Forward Port', 
      description: 'Port for forwarding SuperCollider messages (0 to disable)',
      group: 'SuperCollider',
      min: 0,
      max: 65535
    },
    'sc_backend.FORWARD_ADDRESS': { 
      type: 'string', 
      label: 'Forward Address', 
      description: 'Address for forwarding SuperCollider messages',
      group: 'SuperCollider'
    },
    'sc_backend.ADDRESS': { 
      type: 'string', 
      label: 'SuperCollider Address', 
      description: 'Network address for SuperCollider server',
      group: 'SuperCollider'
    },
    'sc_backend.BOOT_SCLANG_ON_STARTUP': { 
      type: 'boolean', 
      label: 'Boot SCLang on Startup', 
      description: 'Automatically start SuperCollider when Renardo starts',
      group: 'SuperCollider'
    },
    'sc_backend.SC3_PLUGINS': { 
      type: 'boolean', 
      label: 'Use SC3 Plugins', 
      description: 'Enable SuperCollider SC3 plugins',
      group: 'SuperCollider'
    },
    'sc_backend.ACTIVATED_SCCODE_BANKS': { 
      type: 'array', 
      label: 'Activated SC Code Banks', 
      description: 'List of activated SuperCollider code banks',
      group: 'SuperCollider'
    }
  };
  
  // Generate list of settings groups dynamically from schema
  const settingsGroups = [...new Set(Object.values(settingsSchema).map(setting => setting.group))];
  
  // Load settings data
  async function loadSettings() {
    isLoading = true;
    error = null;
    successMessage = '';
    
    try {
      const response = await fetch('/api/settings');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch settings: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.success) {
        settingsData = data.settings;
        // Clear modified settings on load
        modifiedSettings = {};
      } else {
        throw new Error(data.message || 'Unknown error');
      }
    } catch (err) {
      console.error('Error loading settings:', err);
      error = err.message;
    } finally {
      isLoading = false;
    }
  }
  
  // Save a specific setting
  async function saveSetting(key, value) {
    try {
      const response = await fetch(`/api/settings/${key}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ value })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || `Failed to update setting: ${key}`);
      }
      
      // Update local settings data
      updateNestedSetting(settingsData, key, value);
      
      // Remove from modified settings
      delete modifiedSettings[key];
      
      // Show success message
      successMessage = `Setting ${key} updated successfully`;
      setTimeout(() => {
        successMessage = '';
      }, 3000);
      
      return true;
    } catch (err) {
      console.error(`Error saving setting ${key}:`, err);
      error = err.message;
      setTimeout(() => {
        error = null;
      }, 5000);
      return false;
    }
  }
  
  // Handle settings reset
  async function resetSettings() {
    if (!confirm('Are you sure you want to reset all settings to defaults?')) {
      return;
    }
    
    try {
      const response = await fetch('/api/settings/reset', {
        method: 'POST'
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to reset settings');
      }
      
      // Update local settings data
      settingsData = data.settings;
      
      // Clear modified settings
      modifiedSettings = {};
      
      // Show success message
      successMessage = 'All settings reset to defaults';
      setTimeout(() => {
        successMessage = '';
      }, 3000);
    } catch (err) {
      console.error('Error resetting settings:', err);
      error = err.message;
      setTimeout(() => {
        error = null;
      }, 5000);
    }
  }
  
  // Update a setting in the local state
  function handleSettingChange(key, value) {
    // Update modified settings
    modifiedSettings[key] = value;
  }
  
  // Save all modified settings
  async function saveAllChanges() {
    const keys = Object.keys(modifiedSettings);
    if (keys.length === 0) {
      return;
    }
    
    let allSuccess = true;
    
    // Save each modified setting
    for (const key of keys) {
      const success = await saveSetting(key, modifiedSettings[key]);
      if (!success) {
        allSuccess = false;
      }
    }
    
    if (allSuccess) {
      // Clear modified settings
      modifiedSettings = {};
      // Show success message
      successMessage = 'All changes saved successfully';
      setTimeout(() => {
        successMessage = '';
      }, 3000);
    }
  }
  
  // Update a nested setting
  function updateNestedSetting(obj, path, value) {
    const keys = path.split('.');
    let current = obj;
    
    // Navigate to the deepest level
    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i];
      if (!current[key]) {
        current[key] = {};
      }
      current = current[key];
    }
    
    // Set the value
    current[keys[keys.length - 1]] = value;
  }
  
  // Get a nested setting value
  function getNestedSetting(obj, path, defaultValue = undefined) {
    try {
      const keys = path.split('.');
      let current = obj;
      
      for (const key of keys) {
        if (current[key] === undefined) {
          return defaultValue;
        }
        current = current[key];
      }
      
      return current;
    } catch (e) {
      return defaultValue;
    }
  }
  
  // Check if a setting is modified
  function isSettingModified(key) {
    return key in modifiedSettings;
  }
  
  // Get the current value of a setting (modified or from data)
  function getCurrentValue(key) {
    if (isSettingModified(key)) {
      return modifiedSettings[key];
    }
    return getNestedSetting(settingsData, key);
  }
  
  // Check if there are any unsaved changes
  function hasUnsavedChanges() {
    return Object.keys(modifiedSettings).length > 0;
  }
  
  // Listen for WebSocket settings updates
  const unsubscribe = appState.subscribe(state => {
    if (state._lastMessage) {
      // Handle settings updates from WebSocket
      if (state._lastMessage.type === 'setting_updated') {
        const { key, value } = state._lastMessage.data;
        updateNestedSetting(settingsData, key, value);
        
        // Remove from modified settings if it matches
        if (modifiedSettings[key] === value) {
          delete modifiedSettings[key];
        }
      } 
      // Handle settings reset
      else if (state._lastMessage.type === 'settings_reset') {
        settingsData = state._lastMessage.data.settings;
        modifiedSettings = {};
      }
    }
  });
  
  // Load settings on mount
  onMount(() => {
    loadSettings();
  });
  
  // Cleanup on destroy
  onDestroy(() => {
    unsubscribe();
  });
  
  // Prevent navigation if there are unsaved changes
  function handleBeforeUnload(event) {
    if (hasUnsavedChanges()) {
      const message = 'You have unsaved changes. Are you sure you want to leave?';
      event.returnValue = message;
      return message;
    }
  }
  
  // Add beforeunload event listener
  onMount(() => {
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  });
</script>

<main>
  <div class="settings-container">
    <header>
      <h1>Renardo Configuration</h1>
      <p>Manage application settings and preferences</p>
    </header>
    
    {#if isLoading}
      <div class="loading">
        <p>Loading settings...</p>
      </div>
    {:else}
      <!-- Reset and save buttons -->
      <div class="settings-actions">
        <button 
          class="reset-button" 
          on:click={resetSettings}
          disabled={isLoading}
        >
          Reset All Settings
        </button>
        
        <button 
          class="save-button" 
          on:click={saveAllChanges}
          disabled={isLoading || !hasUnsavedChanges()}
        >
          Save Changes {hasUnsavedChanges() ? `(${Object.keys(modifiedSettings).length})` : ''}
        </button>
      </div>
      
      <!-- Status messages -->
      {#if error}
        <div class="error-message" transition:fade={{ duration: 300 }}>
          <p>{error}</p>
        </div>
      {/if}
      
      {#if successMessage}
        <div class="success-message" transition:fade={{ duration: 300 }}>
          <p>{successMessage}</p>
        </div>
      {/if}
      
      <!-- Settings panels organized by group -->
      {#each settingsGroups as group}
        <div class="settings-group">
          <h2>{group}</h2>
          <div class="settings-items">
            {#each Object.entries(settingsSchema).filter(([_, schema]) => schema.group === group) as [key, schema]}
              {@const value = getCurrentValue(key)}
              <div class="setting-item" class:modified={isSettingModified(key)}>
                <div class="setting-info">
                  <label for={key}>{schema.label}</label>
                  <p class="description">{schema.description}</p>
                </div>
                
                <div class="setting-control">
                  {#if schema.type === 'boolean'}
                    <label class="switch">
                      <input 
                        type="checkbox"
                        id={key}
                        checked={value} 
                        on:change={(e) => handleSettingChange(key, e.target.checked)}
                      />
                      <span class="slider"></span>
                    </label>
                  {:else if schema.type === 'number'}
                    <input 
                      type="number"
                      id={key}
                      value={value}
                      min={schema.min}
                      max={schema.max}
                      on:input={(e) => handleSettingChange(key, Number(e.target.value))}
                    />
                  {:else if schema.type === 'string'}
                    <input 
                      type="text"
                      id={key}
                      value={value}
                      on:input={(e) => handleSettingChange(key, e.target.value)}
                    />
                  {:else if schema.type === 'array'}
                    <textarea 
                      id={key}
                      value={Array.isArray(value) ? value.join(', ') : ''} 
                      on:input={(e) => handleSettingChange(key, e.target.value.split(',').map(item => item.trim()))}
                    ></textarea>
                  {/if}
                  
                  {#if isSettingModified(key)}
                    <div class="setting-actions">
                      <button class="save-item-button" on:click={() => saveSetting(key, modifiedSettings[key])}>
                        Save
                      </button>
                      <button class="cancel-button" on:click={() => delete modifiedSettings[key]}>
                        Cancel
                      </button>
                    </div>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/each}
    {/if}
  </div>
</main>

<style>
  main {
    width: 100%;
    padding: 1rem;
  }
  
  .settings-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 1rem;
  }
  
  header {
    margin-bottom: 2rem;
  }
  
  h1 {
    color: #2c3e50;
    margin-bottom: 0.5rem;
  }
  
  header p {
    color: #7f8c8d;
    margin-bottom: 1rem;
  }
  
  .loading {
    text-align: center;
    padding: 2rem;
    color: #666;
  }
  
  .settings-actions {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 6px;
  }
  
  .reset-button {
    background-color: #e74c3c;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .reset-button:hover:not(:disabled) {
    background-color: #c0392b;
  }
  
  .save-button {
    background-color: #2ecc71;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .save-button:hover:not(:disabled) {
    background-color: #27ae60;
  }
  
  button:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
  }
  
  .error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
  
  .success-message {
    background-color: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
  
  .settings-group {
    margin-bottom: 2rem;
    background-color: white;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }
  
  .settings-group h2 {
    font-size: 1.2rem;
    padding: 1rem;
    margin: 0;
    background-color: #f1f2f6;
    border-bottom: 1px solid #ddd;
    color: #2c3e50;
  }
  
  .settings-items {
    padding: 0.5rem;
  }
  
  .setting-item {
    display: flex;
    padding: 1rem;
    border-bottom: 1px solid #eee;
    transition: background-color 0.2s;
  }
  
  .setting-item:last-child {
    border-bottom: none;
  }
  
  .setting-item.modified {
    background-color: #fff8e1;
  }
  
  .setting-info {
    flex: 1;
    padding-right: 1rem;
  }
  
  .setting-info label {
    display: block;
    font-weight: 500;
    margin-bottom: 0.25rem;
    color: #34495e;
  }
  
  .description {
    color: #7f8c8d;
    font-size: 0.9rem;
    margin: 0;
  }
  
  .setting-control {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.5rem;
  }
  
  input[type="text"],
  input[type="number"],
  textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.95rem;
    font-family: inherit;
  }
  
  input[type="text"]:focus,
  input[type="number"]:focus,
  textarea:focus {
    border-color: #3498db;
    outline: none;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }
  
  textarea {
    min-height: 80px;
    resize: vertical;
  }
  
  /* Toggle switch for booleans */
  .switch {
    position: relative;
    display: inline-block;
    width: 60px;
    height: 30px;
  }
  
  .switch input {
    opacity: 0;
    width: 0;
    height: 0;
  }
  
  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: .4s;
    border-radius: 34px;
  }
  
  .slider:before {
    position: absolute;
    content: "";
    height: 22px;
    width: 22px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
  }
  
  input:checked + .slider {
    background-color: #2196F3;
  }
  
  input:focus + .slider {
    box-shadow: 0 0 1px #2196F3;
  }
  
  input:checked + .slider:before {
    transform: translateX(30px);
  }
  
  .setting-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }
  
  .save-item-button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    cursor: pointer;
  }
  
  .save-item-button:hover {
    background-color: #2980b9;
  }
  
  .cancel-button {
    background-color: #95a5a6;
    color: white;
    border: none;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    cursor: pointer;
  }
  
  .cancel-button:hover {
    background-color: #7f8c8d;
  }
  
  @media (max-width: 768px) {
    .setting-item {
      flex-direction: column;
    }
    
    .setting-info {
      padding-right: 0;
      margin-bottom: 1rem;
    }
    
    .setting-control {
      width: 100%;
      align-items: flex-start;
    }
  }
</style>