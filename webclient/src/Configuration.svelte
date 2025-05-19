<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade } from 'svelte/transition';
  import { appState } from './lib/websocket.js';
  
  // State for settings data
  let settingsData = {};
  let isLoading = true;
  let error = null;
  let successMessage = '';
  let showAdvancedView = false;
  
  // User directory state
  let userDirectory = '';
  let isMovingDirectory = false;
  let newUserDirectory = '';
  
  // Track settings that have been modified but not saved
  let modifiedSettings = {};
  
  // Settings schema - provides metadata for each setting
  const settingsSchema = {
    'core.CLOCK_LATENCY': { 
      type: 'number', 
      label: 'Clock Latency', 
      description: 'Latency adjustment for timing in milliseconds',
      group: 'Performance',
      min: 0,
      max: 500
    },
    'samples.SAMPLES_PACK_NUMBER': { 
      type: 'number', 
      label: 'Samples Pack Number', 
      description: 'Number of sample packs to load',
      group: 'Samples',
      min: 0,
      max: 100
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
  
  // Load user directory
  async function loadUserDirectory() {
    try {
      const response = await fetch('/api/settings/user-directory');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch user directory: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.success) {
        userDirectory = data.path;
      } else {
        throw new Error(data.message || 'Unknown error');
      }
    } catch (err) {
      console.error('Error loading user directory:', err);
      error = err.message;
    }
  }
  
  // Open user directory in OS file browser
  async function openUserDirectory() {
    try {
      const response = await fetch('/api/settings/user-directory/open', {
        method: 'POST'
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to open user directory');
      }
      
      successMessage = 'User directory opened';
      setTimeout(() => {
        successMessage = '';
      }, 3000);
    } catch (err) {
      console.error('Error opening user directory:', err);
      error = err.message;
      setTimeout(() => {
        error = null;
      }, 5000);
    }
  }
  
  // Move user directory
  async function moveUserDirectory() {
    if (!newUserDirectory.trim()) {
      error = 'Please enter a new directory path';
      setTimeout(() => {
        error = null;
      }, 3000);
      return;
    }
    
    if (!confirm(`Are you sure you want to move the user directory to:\n${newUserDirectory}?\n\nThis will move all configuration and data files to the new location.`)) {
      return;
    }
    
    isMovingDirectory = true;
    
    try {
      const response = await fetch('/api/settings/user-directory/move', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ path: newUserDirectory })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to move user directory');
      }
      
      userDirectory = data.path;
      newUserDirectory = '';
      
      successMessage = 'User directory moved successfully';
      setTimeout(() => {
        successMessage = '';
      }, 3000);
    } catch (err) {
      console.error('Error moving user directory:', err);
      error = err.message;
      setTimeout(() => {
        error = null;
      }, 5000);
    } finally {
      isMovingDirectory = false;
    }
  }
  
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
    loadUserDirectory();
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

<div class="container mx-auto px-4 py-8 max-w-6xl">
  <div class="text-center mb-8">
    <h1 class="text-3xl font-bold mb-2 title-font">Renardo Configuration</h1>
    <p class="text-base-content/70">Manage application settings and preferences</p>
  </div>

  {#if isLoading}
    <div class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>
  {:else}
    <!-- User Directory Section -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title text-lg mb-4">User Directory</h2>
        
        <div class="space-y-4">
          <div>
            <div class="label">
              <span class="label-text">Current User Directory</span>
            </div>
            <div class="bg-base-200 p-3 rounded-box font-mono text-sm break-all">
              {userDirectory || 'Loading...'}
            </div>
          </div>
          
          <div class="flex flex-wrap gap-2">
            <button
              class="btn btn-primary btn-sm"
              on:click={openUserDirectory}
              disabled={!userDirectory}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Open User Directory
            </button>
            
            <button
              class="btn btn-secondary btn-sm"
              on:click={() => isMovingDirectory = true}
              disabled={!userDirectory}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
              </svg>
              Move User Directory
            </button>
          </div>
          
          {#if isMovingDirectory}
            <div class="alert alert-warning">
              <div class="space-y-3 w-full">
                <p class="font-semibold">Move User Directory</p>
                <p class="text-sm">Enter the new path for the user directory:</p>
                <input
                  type="text"
                  class="input input-bordered w-full"
                  bind:value={newUserDirectory}
                  placeholder="e.g., /home/user/renardo"
                />
                <div class="flex gap-2">
                  <button
                    class="btn btn-primary btn-sm"
                    on:click={moveUserDirectory}
                    disabled={!newUserDirectory.trim()}
                  >
                    Confirm Move
                  </button>
                  <button
                    class="btn btn-ghost btn-sm"
                    on:click={() => {
                      isMovingDirectory = false;
                      newUserDirectory = '';
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>

    <!-- View toggle and actions -->
    <div class="card bg-base-200 mb-6">
      <div class="card-body p-4 sm:p-6">
        <div class="flex flex-col sm:flex-row justify-between gap-4">
          <div class="form-control">
            <label class="label cursor-pointer justify-start gap-2">
              <input
                type="checkbox"
                class="toggle toggle-primary"
                bind:checked={showAdvancedView}
              />
              <span class="label-text">Show All Settings (Advanced)</span>
            </label>
          </div>

          <div class="flex flex-wrap gap-2">
            <button
              class="btn btn-error btn-sm"
              on:click={resetSettings}
              disabled={isLoading}
            >
              Reset All Settings
            </button>

            <button
              class="btn btn-success btn-sm"
              on:click={saveAllChanges}
              disabled={isLoading || !hasUnsavedChanges()}
            >
              {#if hasUnsavedChanges()}
                <div class="badge badge-sm">{Object.keys(modifiedSettings).length}</div>
              {/if}
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Status messages -->
    {#if error}
      <div class="alert alert-error mb-6" transition:fade={{ duration: 300 }}>
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <span>{error}</span>
      </div>
    {/if}

    {#if successMessage}
      <div class="alert alert-success mb-6" transition:fade={{ duration: 300 }}>
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <span>{successMessage}</span>
      </div>
    {/if}

    {#if !showAdvancedView}
      <!-- Standard settings view - organized by group -->
      {#each settingsGroups as group}
        <div class="card bg-base-100 shadow-xl mb-6">
          <div class="card-body p-0">
            <div class="bg-base-200 p-4">
              <h2 class="card-title text-lg">{group}</h2>
            </div>

            <div class="divide-y divide-base-200">
              {#each Object.entries(settingsSchema).filter(([_, schema]) => schema.group === group) as [key, schema]}
                {@const value = getCurrentValue(key)}
                <div class="p-4 {isSettingModified(key) ? 'bg-warning bg-opacity-10' : ''}">
                  <div class="flex flex-col md:flex-row md:items-start gap-4">
                    <div class="flex-1">
                      <label for={key} class="font-medium">{schema.label}</label>
                      <p class="text-sm text-base-content/70 mt-1">{schema.description}</p>
                    </div>

                    <div class="w-full md:w-64 space-y-2">
                      {#if schema.type === 'boolean'}
                        <input
                          type="checkbox"
                          id={key}
                          class="toggle toggle-primary"
                          checked={value}
                          on:change={(e) => handleSettingChange(key, e.target.checked)}
                        />
                      {:else if schema.type === 'number'}
                        <input
                          type="range"
                          id={key}
                          class="range range-primary"
                          value={value}
                          min={schema.min}
                          max={schema.max}
                          on:input={(e) => handleSettingChange(key, Number(e.target.value))}
                        />
                        <div class="flex justify-between text-xs px-1">
                          <span>{schema.min}</span>
                          <span class="font-medium">{value}</span>
                          <span>{schema.max}</span>
                        </div>
                      {:else if schema.type === 'string'}
                        <input
                          type="text"
                          id={key}
                          class="input input-bordered w-full"
                          value={value}
                          on:input={(e) => handleSettingChange(key, e.target.value)}
                        />
                      {:else if schema.type === 'array'}
                        <div class="w-full">
                          <label for={key} class="form-control w-full">
                            <div class="label pt-0">
                              <span class="label-text-alt">Enter values separated by commas</span>
                            </div>
                            <textarea
                            id={key}
                            class="textarea textarea-bordered w-full"
                            value={Array.isArray(value) ? value.join(', ') : ''}
                            on:input={(e) => handleSettingChange(key, e.target.value.split(',').map(item => item.trim()).filter(item => item !== ''))}
                            placeholder="e.g. value1, value2, value3"
                          ></textarea>
                        </div>
                      {/if}

                      {#if isSettingModified(key)}
                        <div class="flex justify-end gap-2 mt-2">
                          <button class="btn btn-xs btn-outline" on:click={() => delete modifiedSettings[key]}>
                            Cancel
                          </button>
                          <button class="btn btn-xs btn-primary" on:click={() => saveSetting(key, modifiedSettings[key])}>
                            Save
                          </button>
                        </div>
                      {/if}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        </div>
      {/each}
    {:else}
      <!-- Advanced view - raw JSON display -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
          <h2 class="card-title">All Settings (Read Only)</h2>
          <div class="mockup-code bg-base-300 text-base-content overflow-x-auto max-h-[600px]">
            <pre><code>{JSON.stringify(settingsData, null, 2)}</code></pre>
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>