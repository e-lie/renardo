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
  let tomlText = '';
  let tomlValidationError = '';
  
  // User directory state
  let userDirectory = '';
  let isMovingDirectory = false;
  let newUserDirectory = '';
  
  // Track settings that have been modified but not saved
  let modifiedSettings = {};
  
  // Generate settings schema dynamically based on settings structure
  function generateSettingsSchema() {
    const schema = {};
    
    if (!settingsData || Object.keys(settingsData).length === 0) {
      return schema;
    }
    
    // Process each top-level section
    for (const section in settingsData) {
      const sectionData = settingsData[section];
      
      // Process each setting in the section
      for (const key in sectionData) {
        const fullKey = `${section}.${key}`;
        const value = sectionData[key];
        const valueType = typeof value;
        
        const setting = {
          type: Array.isArray(value) ? 'array' : valueType,
          label: key.split('_').map(word => word.charAt(0) + word.slice(1).toLowerCase()).join(' '),
          description: getSettingDescription(fullKey),
          group: section.charAt(0).toUpperCase() + section.slice(1),
        };
        
        // Add min/max for number types
        if (valueType === 'number') {
          // Set reasonable min/max based on the value
          if (['latency', 'delay', 'timeout'].some(term => key.toLowerCase().includes(term))) {
            setting.min = 0;
            setting.max = Math.max(500, value * 2);
          } else if (key.includes('VOLUME') || key.includes('GAIN')) {
            setting.min = 0;
            setting.max = 1;
            setting.step = 0.01;
          } else if (key.includes('LEVEL') || key.includes('AMPLITUDE')) {
            setting.min = 0;
            setting.max = 1;
            setting.step = 0.01;
          } else if (key.includes('SPEED') || key.includes('RATE')) {
            setting.min = 0.25;
            setting.max = 4;
            setting.step = 0.25;
          } else {
            setting.min = 0;
            setting.max = Math.max(100, value * 2);
          }
        } else if (setting.type === 'array') {
          // No special handling needed for arrays
        } else if (setting.type === 'boolean') {
          // No special handling needed for booleans
        }
        
        schema[fullKey] = setting;
      }
    }
    
    return schema;
  }
  
  // Get a descriptive text for a setting based on its key
  function getSettingDescription(key) {
    const descriptions = {
      'core.CLOCK_LATENCY': 'Latency adjustment for timing in milliseconds',
      'core.DEFAULT_SAMPLE_RATE': 'Default sample rate for audio processing',
      'core.COLLECTIONS_DOWNLOAD_SERVER': 'Server URL for downloading collections',
      'samples.SAMPLES_PACK_NUMBER': 'Number of sample packs to load',
      'samples.SAMPLES_PACK_LOADED': 'Names of sample packs that are loaded',
      'sc_backend.ACTIVATED_SCCODE_BANKS': 'List of activated SuperCollider code banks',
      'reaper_backend.ACTIVATED_REAPER_BANKS': 'List of activated Reaper banks',
      'reaper_backend.SELECTED_REAPER_INSTRUMENTS': 'List of selected Reaper instruments to load',
      'webserver.PORT': 'Port number for the web server',
      'webserver.ENABLED': 'Whether the web server is enabled',
      'webserver.HOST': 'Host address for the web server',
    };
    
    // If we have a specific description, use it
    if (descriptions[key]) {
      return descriptions[key];
    }
    
    // Generate a generic description based on the key
    const parts = key.split('.');
    const settingName = parts[1];
    const words = settingName.split('_');
    const readableName = words.map(word => word.charAt(0) + word.slice(1).toLowerCase()).join(' ');
    
    return `Configure the ${readableName} setting for ${parts[0]}`;
  }
  
  // Settings schema generated dynamically
  $: settingsSchema = generateSettingsSchema();
  
  // Generate list of settings groups dynamically from schema
  $: settingsGroups = [...new Set(Object.values(settingsSchema).map(setting => setting.group))];

  // Load TOML when advanced view is opened
  $: if (showAdvancedView && !tomlText) {
    loadTomlSettings();
  }
  
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
  
  // Load raw TOML settings text
  async function loadTomlSettings() {
    try {
      const response = await fetch('/api/settings/toml');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch TOML settings: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      if (data.success) {
        tomlText = data.toml;
      } else {
        throw new Error(data.message || 'Failed to load TOML settings');
      }
    } catch (err) {
      console.error('Error loading TOML settings:', err);
      // Fallback to empty TOML if loading fails
      tomlText = '';
    }
  }
  
  // Save TOML settings directly
  async function saveTomlSettings() {
    tomlValidationError = '';
    
    try {
      const response = await fetch('/api/settings/toml', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ toml: tomlText })
      });
      
      const data = await response.json();
      
      if (!response.ok || !data.success) {
        if (data.validation_error) {
          tomlValidationError = data.validation_error;
          throw new Error(`TOML Validation Error: ${data.validation_error}`);
        } else {
          throw new Error(data.message || 'Failed to save TOML settings');
        }
      }
      
      // Reload settings after successful save
      await loadSettings();
      
      // Show success message
      successMessage = 'TOML settings saved successfully';
      setTimeout(() => {
        successMessage = '';
      }, 3000);
      
      return true;
    } catch (err) {
      console.error('Error saving TOML settings:', err);
      error = err.message;
      setTimeout(() => {
        error = null;
      }, 5000);
      return false;
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
    
    // Special case for full JSON settings from advanced view
    if (keys.includes('_json_full_settings')) {
      try {
        // Create an array of promises for each top-level section
        const fullSettings = modifiedSettings['_json_full_settings'];
        const promises = [];
        
        // For each section, update all its settings
        for (const section in fullSettings) {
          const sectionData = fullSettings[section];
          
          // For each setting in the section
          for (const key in sectionData) {
            const fullKey = `${section}.${key}`;
            const value = sectionData[key];
            
            // Queue up a save operation
            promises.push(
              saveSetting(fullKey, value)
                .catch(err => {
                  console.error(`Error saving setting ${fullKey}:`, err);
                  allSuccess = false;
                  return false;
                })
            );
          }
        }
        
        // Wait for all settings to be saved
        await Promise.all(promises);
        
        if (allSuccess) {
          // Reload settings to get the fresh state
          await loadSettings();
          
          // Show success message
          successMessage = 'All changes from JSON editor saved successfully';
          setTimeout(() => {
            successMessage = '';
          }, 3000);
        }
      } catch (err) {
        console.error('Error saving JSON settings:', err);
        error = `Error saving JSON settings: ${err.message}`;
        allSuccess = false;
      }
    } else {
      // Normal case: save each modified setting
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
      <!-- Advanced view - editable TOML display -->
      <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
          <div class="flex justify-between items-center mb-4">
            <h2 class="card-title">All Settings (TOML Editor)</h2>
            
            <div class="flex gap-2">
              <button 
                class="btn btn-sm btn-secondary" 
                on:click={loadTomlSettings}
              >
                Reload TOML
              </button>
              <button 
                class="btn btn-sm btn-primary" 
                on:click={saveTomlSettings}
                disabled={!tomlText.trim()}
              >
                Save TOML
              </button>
            </div>
          </div>
          
          <!-- Warning message -->
          <div class="alert alert-warning mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            <div>
              <span class="font-bold">Advanced Mode</span>
              <p class="text-sm">Edit the TOML configuration directly. Invalid TOML syntax will be validated on the backend before saving.</p>
            </div>
          </div>
          
          <!-- TOML validation error display -->
          {#if tomlValidationError}
            <div class="alert alert-error mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <div>
                <span class="font-bold">TOML Validation Error</span>
                <p class="text-sm">{tomlValidationError}</p>
              </div>
            </div>
          {/if}
          
          <!-- TOML Editor -->
          <div class="form-control w-full">
            <textarea 
              class="textarea textarea-bordered font-mono text-sm h-[600px] w-full"
              bind:value={tomlText}
              spellcheck="false"
              placeholder="Loading TOML settings..."
            ></textarea>
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>