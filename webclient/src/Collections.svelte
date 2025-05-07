<script>
  import { onMount, onDestroy } from 'svelte';
  import { appState } from './lib/websocket.js';
  
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

<main>
  <div class="collections-container">
    <header>
      <h1>Additional Collections</h1>
      <p>
        Download additional sample packs and instruments from the Renardo collections server.
      </p>
      
      {#if collectionsData}
        <div class="server-info">
          <p>Collection Server: <code>{collectionsData.collections_server}</code></p>
        </div>
      {/if}
      
      <div class="collections-actions">
        <button 
          class="refresh-button" 
          on:click={refreshCollections} 
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Refresh Collections'}
        </button>
      </div>
    </header>
    
    {#if error}
      <div class="error-message">
        <p>Error loading collections: {error}</p>
        <p>Please check your internet connection and try again.</p>
      </div>
    {/if}
    
    {#if isLoading}
      <div class="loading">
        <p>Loading collections data...</p>
      </div>
    {:else if collectionsData}
      <div class="collections-section">
        <h2>Sample Packs</h2>
        
        {#if collectionsData.samples && collectionsData.samples.length > 0}
          <div class="collections-grid">
            {#each collectionsData.samples as sample}
              <div class="collection-card {sample.installed ? 'installed' : ''}">
                <div class="collection-header">
                  <h3>{sample.name}</h3>
                  {#if sample.is_default}
                    <span class="default-badge">Default</span>
                  {/if}
                </div>
                
                <div class="collection-info">
                  <p class="description">{sample.description || 'No description available'}</p>
                  <p class="meta">
                    <span class="author">By {sample.author || 'Unknown'}</span>
                    <span class="version">v{sample.version || '1.0'}</span>
                    <span class="size">{formatFileSize(sample.size)}</span>
                  </p>
                  {#if sample.tags && sample.tags.length > 0}
                    <div class="tags">
                      {#each sample.tags as tag}
                        <span class="tag">{tag}</span>
                      {/each}
                    </div>
                  {/if}
                </div>
                
                <div class="collection-actions">
                  {#if sample.installed}
                    <span class="status-installed">Installed</span>
                  {:else if downloadsInProgress.has(`samples-${sample.name}`)}
                    <button class="download-button" disabled>Downloading...</button>
                  {:else}
                    <button 
                      class="download-button" 
                      on:click={() => downloadCollection('samples', sample.name)}
                    >
                      Download
                    </button>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <p class="no-collections">No sample packs available.</p>
        {/if}
      </div>
      
      <div class="collections-section">
        <h2>Instrument Packs</h2>
        
        {#if collectionsData.sccode && collectionsData.sccode.length > 0}
          <div class="collections-grid">
            {#each collectionsData.sccode as sccode}
              <div class="collection-card {sccode.installed ? 'installed' : ''}">
                <div class="collection-header">
                  <h3>{sccode.name}</h3>
                  {#if sccode.is_default}
                    <span class="default-badge">Default</span>
                  {/if}
                </div>
                
                <div class="collection-info">
                  <p class="description">{sccode.description || 'No description available'}</p>
                  <p class="meta">
                    <span class="author">By {sccode.author || 'Unknown'}</span>
                    <span class="version">v{sccode.version || '1.0'}</span>
                    <span class="size">{formatFileSize(sccode.size)}</span>
                  </p>
                  {#if sccode.tags && sccode.tags.length > 0}
                    <div class="tags">
                      {#each sccode.tags as tag}
                        <span class="tag">{tag}</span>
                      {/each}
                    </div>
                  {/if}
                </div>
                
                <div class="collection-actions">
                  {#if sccode.installed}
                    <span class="status-installed">Installed</span>
                  {:else if downloadsInProgress.has(`sccode-${sccode.name}`)}
                    <button class="download-button" disabled>Downloading...</button>
                  {:else}
                    <button 
                      class="download-button" 
                      on:click={() => downloadCollection('sccode', sccode.name)}
                    >
                      Download
                    </button>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <p class="no-collections">No instrument packs available.</p>
        {/if}
      </div>
    {/if}
  </div>
  
  <!-- Download progress logger -->
  {#if showLogger}
    <div class="logger-overlay">
      <div class="logger-panel">
        <div class="logger-header">
          <h3>Download Progress</h3>
          <div class="ws-status">
            {#if wsConnected}
              <span class="ws-status-connected">Connected</span>
            {:else}
              <span class="ws-status-disconnected">Disconnected</span>
            {/if}
          </div>
          <button class="close-button" on:click={closeLogger}>×</button>
        </div>
        <div id="log-container" class="logger-content">
          {#if !wsConnected}
            <div class="log-message log-error">
              <span class="log-timestamp">{new Date().toLocaleTimeString()}</span>
              <span class="log-text">WebSocket disconnected. Waiting for reconnection...</span>
            </div>
          {/if}
          
          {#if logMessages.length === 0}
            <p class="log-empty">Waiting for download to start...</p>
          {:else}
            {#each logMessages as log}
              <div class="log-message log-{log.level.toLowerCase()}">
                <span class="log-timestamp">{log.timestamp}</span>
                <span class="log-text">{log.message}</span>
              </div>
            {/each}
          {/if}
        </div>
      </div>
    </div>
  {/if}
</main>

<style>
  main {
    width: 100%;
    height: 100%;
    padding: 1rem;
    overflow-y: auto;
  }
  
  .collections-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }
  
  header {
    margin-bottom: 2rem;
  }
  
  h1 {
    margin-bottom: 0.5rem;
    color: #333;
  }
  
  header p {
    margin-bottom: 1rem;
    color: #666;
  }
  
  .server-info {
    background-color: #f5f5f5;
    padding: 0.5rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
  
  .server-info code {
    font-family: monospace;
    background-color: #e5e5e5;
    padding: 0.2rem 0.4rem;
    border-radius: 2px;
  }
  
  .collections-actions {
    margin-bottom: 1rem;
  }
  
  .refresh-button {
    background-color: #2c3e50;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .refresh-button:hover:not(:disabled) {
    background-color: #34495e;
  }
  
  .refresh-button:disabled {
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
  
  .loading {
    text-align: center;
    padding: 2rem;
    color: #666;
  }
  
  .collections-section {
    margin-bottom: 2rem;
  }
  
  h2 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #2c3e50;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.5rem;
  }
  
  .collections-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }
  
  .collection-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    background-color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
  }
  
  .collection-card.installed {
    border-color: #2ecc71;
    background-color: #f8fff8;
  }
  
  .collection-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  
  .collection-header h3 {
    margin: 0;
    font-size: 1.2rem;
    color: #2c3e50;
  }
  
  .default-badge {
    background-color: #3498db;
    color: white;
    font-size: 0.7rem;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
  }
  
  .collection-info {
    flex-grow: 1;
    margin-bottom: 1rem;
  }
  
  .description {
    color: #666;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
  }
  
  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    font-size: 0.8rem;
    color: #777;
    margin-bottom: 0.5rem;
  }
  
  .author, .version, .size {
    display: inline-block;
    background-color: #f5f5f5;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
  }
  
  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  
  .tag {
    background-color: #e5e5e5;
    font-size: 0.7rem;
    padding: 0.1rem 0.3rem;
    border-radius: 4px;
    color: #666;
  }
  
  .collection-actions {
    margin-top: auto;
    text-align: right;
  }
  
  .download-button {
    background-color: #27ae60;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .download-button:hover:not(:disabled) {
    background-color: #2ecc71;
  }
  
  .download-button:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
  }
  
  .status-installed {
    color: #27ae60;
    font-weight: bold;
  }
  
  .no-collections {
    color: #777;
    font-style: italic;
    padding: 1rem;
    text-align: center;
    border: 1px dashed #ddd;
    border-radius: 4px;
  }
  
  /* Logger Styles */
  .logger-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .logger-panel {
    width: 80%;
    max-width: 800px;
    height: 70%;
    max-height: 600px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .logger-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 1rem;
    border-bottom: 1px solid #ddd;
    background-color: #f5f5f5;
  }
  
  .logger-header h3 {
    margin: 0;
    color: #2c3e50;
    flex: 1;
  }
  
  .ws-status {
    display: flex;
    align-items: center;
    margin-right: 1rem;
    font-size: 0.8rem;
  }
  
  .ws-status-connected {
    color: #27ae60;
    background-color: #eafaf1;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
  }
  
  .ws-status-connected::before {
    content: "";
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: #27ae60;
    border-radius: 50%;
    margin-right: 5px;
  }
  
  .ws-status-disconnected {
    color: #e74c3c;
    background-color: #fdedec;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
  }
  
  .ws-status-disconnected::before {
    content: "";
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: #e74c3c;
    border-radius: 50%;
    margin-right: 5px;
  }
  
  .close-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #666;
    cursor: pointer;
    padding: 0;
    line-height: 1;
  }
  
  .close-button:hover {
    color: #e74c3c;
  }
  
  .logger-content {
    flex-grow: 1;
    padding: 1rem;
    overflow-y: auto;
    font-family: monospace;
    font-size: 0.9rem;
    background-color: #f8f8f8;
  }
  
  .log-empty {
    color: #888;
    font-style: italic;
    text-align: center;
    margin: 2rem 0;
  }
  
  .log-message {
    margin-bottom: 0.3rem;
    padding: 0.3rem 0.5rem;
    border-radius: 4px;
    background-color: #fff;
    display: flex;
    align-items: flex-start;
  }
  
  .log-info {
    border-left: 3px solid #3498db;
  }
  
  .log-warn {
    border-left: 3px solid #f39c12;
    background-color: #fffbf0;
  }
  
  .log-error {
    border-left: 3px solid #e74c3c;
    background-color: #fff0f0;
  }
  
  .log-success {
    border-left: 3px solid #2ecc71;
    background-color: #f0fff0;
  }
  
  /* Highlight animation for important messages */
  .log-highlight {
    animation: log-highlight-pulse 2s ease-in-out;
  }
  
  @keyframes log-highlight-pulse {
    0% { transform: scale(1); }
    10% { transform: scale(1.02); box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    20% { transform: scale(1); }
  }
  
  .log-timestamp {
    font-size: 0.8rem;
    color: #777;
    margin-right: 0.5rem;
    min-width: 70px;
  }
  
  .log-text {
    flex-grow: 1;
    word-break: break-word;  /* Allow long words to break */
  }
  
  @media (max-width: 768px) {
    .collections-grid {
      grid-template-columns: 1fr;
    }
    
    .logger-panel {
      width: 95%;
      height: 80%;
    }
  }
</style>