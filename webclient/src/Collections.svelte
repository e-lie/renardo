<script>
  import { onMount, onDestroy } from 'svelte';
  import { appState } from './lib/websocket.js';
  import ExploreCollectionModal from './lib/ExploreCollectionModal.svelte';
  
  // State for collections data
  let collectionsData = null;
  let isLoading = true;
  let error = null;
  
  // State for downloads in progress
  let downloadsInProgress = new Map();
  
  // Logger state
  let showLogger = false;
  let logMessages = [];
  let unsubscribeFromLogs;
  let unsubscribeDownloadComplete;
  
  // WebSocket connection state
  let wsConnected = false;
  
  // Explore modal state
  let showExploreModal = false;
  let exploreCollectionType = '';
  let exploreCollectionName = '';
  
  // Subscribe to connection status
  const unsubscribeWS = appState.subscribe(state => {
    wsConnected = state.connected;
    
    // If we just connected and already have a logger open, refresh log messages
    if (wsConnected && showLogger && logMessages.length === 0) {
      // Add connection status message to logs
      logMessages = [...logMessages, {
        timestamp: new Date().toLocaleTimeString(),
        level: 'INFO',
        message: 'WebSocket connection established'
      }];
    }
  });
  
  // Formats file size for display
  function formatFileSize(size) {
    if (!size || size === 'Unknown') return 'Unknown size';
    
    if (typeof size === 'string') {
      // Try to convert to number if it's a string
      size = parseInt(size, 10);
      if (isNaN(size)) return 'Unknown size';
    }
    
    const units = ['B', 'KB', 'MB', 'GB'];
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  }
  
  // Load collections data
  async function loadCollections() {
    isLoading = true;
    error = null;
    
    try {
      const response = await fetch('/api/collections');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch collections: ${response.status} ${response.statusText}`);
      }
      
      collectionsData = await response.json();
    } catch (err) {
      console.error('Error loading collections:', err);
      error = err.message;
    } finally {
      isLoading = false;
    }
  }
  
  // Download a collection
  async function downloadCollection(type, name) {
    // Clear previous logs
    logMessages = [];
    
    // Show logger
    showLogger = true;
    
    // Set download in progress
    downloadsInProgress.set(`${type}-${name}`, true);
    downloadsInProgress = downloadsInProgress; // trigger reactivity
    
    // Clean up any existing subscription
    if (unsubscribeFromLogs) {
      unsubscribeFromLogs();
      unsubscribeFromLogs = null;
    }
    
    // Setup subscription for the app state to get log messages and download status
    let previousLogCount = 0;
    
    unsubscribeFromLogs = appState.subscribe(state => {
      // Handle websocket log messages - get any new ones from the store
      if (state.logMessages && state.logMessages.length > previousLogCount) {
        // Get only the new messages since our last check
        const newMessages = state.logMessages.slice(previousLogCount);
        previousLogCount = state.logMessages.length;
        
        // Add new messages to our local log display
        for (const logMsg of newMessages) {
          logMessages = [...logMessages, logMsg];
          
          console.log('New log message:', logMsg); // Debug logging
          
          // If this is a success or error message, make it more prominent
          if (logMsg.level === 'SUCCESS' || logMsg.level === 'ERROR') {
            // Schedule this after the DOM has been updated
            setTimeout(() => {
              const logContainer = document.getElementById('log-container');
              if (logContainer) {
                const lastMessageEl = logContainer.lastElementChild;
                if (lastMessageEl) {
                  lastMessageEl.classList.add('log-highlight');
                  setTimeout(() => {
                    lastMessageEl.classList.remove('log-highlight');
                  }, 2000);
                }
              }
            }, 50);
          }
        }
        
        // Auto-scroll the log container to the bottom after messages are added
        setTimeout(() => {
          const logContainer = document.getElementById('log-container');
          if (logContainer) {
            logContainer.scrollTo({
              top: logContainer.scrollHeight,
              behavior: 'smooth'
            });
          }
        }, 50);
      }
    });
    
    // Separate listener specifically for collection download completion events
    const unsubscribeDownloadComplete = appState.subscribe(state => {
      if (state._lastMessage && state._lastMessage.type === 'collection_downloaded' && 
          state._lastMessage.data && state._lastMessage.data.type === type && 
          state._lastMessage.data.name === name) {
          
        // Download complete
        if (state._lastMessage.data.success) {
          // Update UI to show as installed
          if (collectionsData && collectionsData[type]) {
            const collection = collectionsData[type].find(c => c.name === name);
            if (collection) {
              collection.installed = true;
            }
            collectionsData = { ...collectionsData };
          }
        }
        
        // Remove from downloads in progress
        downloadsInProgress.delete(`${type}-${name}`);
        downloadsInProgress = downloadsInProgress; // trigger reactivity
      }
    });
    
    try {
      // Log the start of the request locally to provide immediate feedback
      logMessages = [...logMessages, {
        timestamp: new Date().toLocaleTimeString(),
        level: 'INFO',
        message: `Initiating download request for ${type}/${name}...`
      }];
      
      // Also add a check if we're connected to websocket
      if (!wsConnected) {
        logMessages = [...logMessages, {
          timestamp: new Date().toLocaleTimeString(),
          level: 'WARN',
          message: `WebSocket is disconnected. Progress updates may not appear in real-time.`
        }];
      }
      
      const response = await fetch(`/api/collections/${type}/${name}/download`, {
        method: 'POST'
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || `Failed to download ${type} "${name}"`);
      }
      
      // Confirm API response in the log for user visibility
      logMessages = [...logMessages, {
        timestamp: new Date().toLocaleTimeString(),
        level: 'INFO',
        message: `Server responded: ${data.message || 'Download started'}`
      }];
      
      // If already installed, no need to keep the UI in loading state
      if (data.already_installed) {
        downloadsInProgress.delete(`${type}-${name}`);
        downloadsInProgress = downloadsInProgress; // trigger reactivity
        
        // Update UI
        if (collectionsData && collectionsData[type]) {
          const collection = collectionsData[type].find(c => c.name === name);
          if (collection) {
            collection.installed = true;
          }
          collectionsData = { ...collectionsData };
        }
      }
      
    } catch (err) {
      console.error(`Error downloading ${type} "${name}":`, err);
      
      // Add error to log
      logMessages = [...logMessages, {
        timestamp: new Date().toLocaleTimeString(),
        level: 'ERROR',
        message: `Error: ${err.message}`
      }];
      
      // Remove from downloads in progress
      downloadsInProgress.delete(`${type}-${name}`);
      downloadsInProgress = downloadsInProgress; // trigger reactivity
    }
  }
  
  // Refresh collections data
  function refreshCollections() {
    loadCollections();
  }
  
  // Close logger panel
  function closeLogger() {
    showLogger = false;
    
    // Unsubscribe from log messages when closing logger
    if (unsubscribeFromLogs) {
      unsubscribeFromLogs();
      unsubscribeFromLogs = null;
    }
  }
  
  // Open explore modal
  function openExploreModal(type, name) {
    exploreCollectionType = type;
    exploreCollectionName = name;
    showExploreModal = true;
  }
  
  // Close explore modal
  function closeExploreModal() {
    showExploreModal = false;
  }
  
  // Load collections on mount
  onMount(() => {
    loadCollections();
  });
  
  // Cleanup on destroy
  onDestroy(() => {
    if (unsubscribeFromLogs) {
      unsubscribeFromLogs();
    }
    
    if (unsubscribeDownloadComplete) {
      unsubscribeDownloadComplete();
    }
    
    if (unsubscribeWS) {
      unsubscribeWS();
    }
  });
</script>

<div class="container mx-auto px-4 py-8 max-w-6xl">
  <div class="text-center mb-8">
    <h1 class="text-3xl font-bold mb-2 title-font">Additional Collections</h1>
    <p class="text-base-content/70">
      Download additional sample packs and instruments from the Renardo collections server.
    </p>
  </div>

  <!-- Server Information Card -->
  {#if collectionsData}
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <div class="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div class="flex items-center gap-2">
            <div>
              <h2 class="card-title title-font">Collection Server</h2>
              <div class="badge badge-neutral font-mono">{collectionsData.collections_server}</div>
            </div>
          </div>

          <div>
            <button
              class="btn btn-primary"
              on:click={refreshCollections}
              disabled={isLoading}
            >
              {#if isLoading}
                <span class="loading loading-spinner loading-xs"></span>
              {/if}
              {isLoading ? 'Loading...' : 'Refresh Collections'}
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- Error messages -->
  {#if error}
    <div class="alert alert-error mb-8">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
      <div>
        <div class="font-medium">Error loading collections</div>
        <div class="text-sm">{error}</div>
        <div class="text-sm">Please check your internet connection and try again.</div>
      </div>
    </div>
  {/if}

  {#if isLoading}
    <div class="flex justify-center py-12">
      <span class="loading loading-dots loading-lg text-primary"></span>
    </div>
  {:else if collectionsData}
    <!-- Sample Packs Section -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body p-0">
        <div class="bg-base p-4">
          <h2 class="card-title text-primary title-font">Sample Packs >></h2>
        </div>

        <div class="p-4">
          {#if collectionsData.samples && collectionsData.samples.length > 0}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              {#each collectionsData.samples as sample}
                <div class="card bg-base-200 {sample.installed ? 'border-l-4 border-success' : ''}">
                  <div class="card-body">
                    <div class="flex justify-between items-center">
                      <h4 class="card-title text-lg title-font">{sample.name}</h4>
                      {#if sample.is_default}
                        <div class="badge badge-primary">Default</div>
                      {/if}
                    </div>

                    <p class="text-base-content/70 text-sm">{sample.description || 'No description available'}</p>

                    <div class="flex flex-wrap gap-2 my-2">
                      <div class="badge badge-outline badge-sm">By {sample.author || 'Unknown'}</div>
                      <div class="badge badge-outline badge-sm">v{sample.version || '1.0'}</div>
                      <div class="badge badge-outline badge-sm">{formatFileSize(sample.size)}</div>
                    </div>

                    {#if sample.tags && sample.tags.length > 0}
                      <div class="flex flex-wrap gap-1 mt-1">
                        {#each sample.tags as tag}
                          <div class="badge badge-ghost badge-sm">{tag}</div>
                        {/each}
                      </div>
                    {/if}

                    <div class="card-actions justify-end mt-4">
                      {#if sample.installed}
                        <div class="badge badge-success gap-2">
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Installed
                        </div>
                      {:else if downloadsInProgress.has(`samples-${sample.name}`)}
                        <button class="btn btn-primary btn-sm" disabled>
                          <span class="loading loading-spinner loading-xs"></span>
                          Downloading...
                        </button>
                      {:else}
                        <button
                          class="btn btn-primary btn-sm"
                          on:click={() => downloadCollection('samples', sample.name)}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                          </svg>
                          Download
                        </button>
                      {/if}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <div class="card bg-base-200 my-4">
              <div class="card-body items-center text-center">
                <p class="text-base-content/50 italic">No sample packs available.</p>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>

    <!-- Instrument Packs Section -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body p-0">
        <div class="bg-base p-4">
          <h2 class="card-title text-accent title-font">Instrument Packs >></h2>
        </div>

        <div class="p-4">
          {#if collectionsData.sccode && collectionsData.sccode.length > 0}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              {#each collectionsData.sccode as sccode}
                <div class="card bg-base-200 {sccode.installed ? 'border-l-4 border-success' : ''}">
                  <div class="card-body">
                    <div class="flex justify-between items-center">
                      <h4 class="card-title text-lg title-font">{sccode.name}</h4>
                      {#if sccode.is_default}
                        <div class="badge badge-accent">Default</div>
                      {/if}
                    </div>

                    <p class="text-base-content/70 text-sm">{sccode.description || 'No description available'}</p>

                    <div class="flex flex-wrap gap-2 my-2">
                      <div class="badge badge-outline badge-sm">By {sccode.author || 'Unknown'}</div>
                      <div class="badge badge-outline badge-sm">v{sccode.version || '1.0'}</div>
                      <div class="badge badge-outline badge-sm">{formatFileSize(sccode.size)}</div>
                    </div>

                    {#if sccode.tags && sccode.tags.length > 0}
                      <div class="flex flex-wrap gap-1 mt-1">
                        {#each sccode.tags as tag}
                          <div class="badge badge-ghost badge-sm">{tag}</div>
                        {/each}
                      </div>
                    {/if}

                    <div class="card-actions justify-end mt-4">
                      {#if sccode.installed}
                        <div class="badge badge-success gap-2">
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Installed
                        </div>
                      {:else if downloadsInProgress.has(`sccode-${sccode.name}`)}
                        <button class="btn btn-accent btn-sm" disabled>
                          <span class="loading loading-spinner loading-xs"></span>
                          Downloading...
                        </button>
                      {:else}
                        <button
                          class="btn btn-accent btn-sm"
                          on:click={() => downloadCollection('sccode', sccode.name)}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                          </svg>
                          Download
                        </button>
                      {/if}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <div class="card bg-base-200 my-4">
              <div class="card-body items-center text-center">
                <p class="text-base-content/50 italic">No instrument packs available.</p>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
    
    <!-- Reaper Resources Section -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body p-0">
        <div class="bg-base p-4">
          <h2 class="card-title text-secondary title-font">Reaper Resources >></h2>
        </div>

        <div class="p-4">
          {#if collectionsData.reaper && collectionsData.reaper.length > 0}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              {#each collectionsData.reaper as reaper}
                <div 
                  class="card bg-base-200 {reaper.installed ? 'border-l-4 border-success' : ''} hover:shadow-xl hover:scale-[1.02] hover:bg-base-300 transition-all duration-200 cursor-pointer relative group"
                  on:click={() => openExploreModal('reaper', reaper.name)}
                  on:keydown={(e) => e.key === 'Enter' && openExploreModal('reaper', reaper.name)}
                  tabindex="0"
                  role="button"
                  aria-label="Open {reaper.name} collection details"
                >
                  <!-- Explore badge that appears on hover -->
                  <div class="absolute top-2 right-2 badge badge-primary opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Explore
                  </div>
                  <div class="card-body">
                    <div class="flex justify-between items-center">
                      <h4 class="card-title text-lg title-font">{reaper.name}</h4>
                      {#if reaper.is_default}
                        <div class="badge badge-secondary">Default</div>
                      {/if}
                    </div>

                    <p class="text-base-content/70 text-sm">{reaper.description || 'No description available'}</p>

                    <div class="flex flex-wrap gap-2 my-2">
                      <div class="badge badge-outline badge-sm">By {reaper.author || 'Unknown'}</div>
                      <div class="badge badge-outline badge-sm">v{reaper.version || '1.0'}</div>
                      <div class="badge badge-outline badge-sm">{formatFileSize(reaper.size)}</div>
                    </div>

                    {#if reaper.tags && reaper.tags.length > 0}
                      <div class="flex flex-wrap gap-1 mt-1">
                        {#each reaper.tags as tag}
                          <div class="badge badge-ghost badge-sm">{tag}</div>
                        {/each}
                      </div>
                    {/if}

                    <div 
                      class="card-actions justify-end mt-4" 
                      on:click|stopPropagation 
                      on:keydown|stopPropagation
                      role="group"
                      aria-label="Collection actions">
                      {#if reaper.installed}
                        <div class="badge badge-success gap-2">
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Installed
                        </div>
                      {:else if downloadsInProgress.has(`reaper-${reaper.name}`)}
                        <button class="btn btn-secondary btn-sm" disabled>
                          <span class="loading loading-spinner loading-xs"></span>
                          Downloading...
                        </button>
                      {:else}
                        <button
                          class="btn btn-secondary btn-sm"
                          on:click={() => downloadCollection('reaper', reaper.name)}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                          </svg>
                          Download
                        </button>
                      {/if}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <div class="card bg-base-200 my-4">
              <div class="card-body items-center text-center">
                <p class="text-base-content/50 italic">No Reaper resources available.</p>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  {/if}

  <!-- Download progress logger modal -->
  {#if showLogger}
    <div class="modal modal-open">
      <div class="modal-box w-11/12 max-w-6xl h-auto max-h-[90vh]">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-bold text-2xl title-font">Download Progress</h3>

          {#if wsConnected}
            <div class="badge badge-success gap-2">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 bg-success"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-success"></span>
              </span>
              Connected
            </div>
          {:else}
            <div class="badge badge-error gap-2">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 bg-error"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-error"></span>
              </span>
              Disconnected
            </div>
          {/if}
        </div>

        <div id="log-container" class="bg-base-300 p-6 rounded-lg font-mono text-sm h-[600px] overflow-y-auto mb-4 shadow-inner">
          {#if !wsConnected}
            <div class="text-error p-2 mb-2 flex gap-2 bg-error bg-opacity-5 rounded border-l-4 border-error">
              <span class="text-xs opacity-70">{new Date().toLocaleTimeString()}</span>
              <span>WebSocket disconnected. Waiting for reconnection...</span>
            </div>
          {/if}

          {#if logMessages.length === 0}
            <div class="flex flex-col items-center justify-center h-full">
              <span class="loading loading-dots loading-md text-primary"></span>
              <p class="text-center opacity-50 italic mt-4">Waiting for download to start...</p>
            </div>
          {:else}
            {#each logMessages as log}
              <div class="mb-2 pb-2 border-b border-base-200 border-opacity-30 {log.level.toLowerCase() === 'error' ? 'text-error bg-error bg-opacity-5 p-2 rounded' : log.level.toLowerCase() === 'warn' ? 'text-warning' : log.level.toLowerCase() === 'success' ? 'text-success bg-success bg-opacity-5 p-2 rounded' : ''}">
                <span class="text-xs opacity-70 inline-block w-24 mr-2">{log.timestamp}</span>
                <span class="font-medium">{log.message}</span>
              </div>
            {/each}
          {/if}
        </div>

        <div class="modal-action">
          <button class="btn btn-primary btn-lg" on:click={closeLogger}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-1">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Close
          </button>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Explore Collection Modal -->
  <ExploreCollectionModal
    show={showExploreModal}
    collectionType={exploreCollectionType}
    collectionName={exploreCollectionName}
    onClose={closeExploreModal}
  />
</div>