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
    
    try {
      const response = await fetch(`/api/collections/${type}/${name}/download`, {
        method: 'POST'
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || `Failed to download ${type} "${name}"`);
      }
      
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
      
      // Subscribe to log messages for download progress updates
      if (!unsubscribeFromLogs) {
        unsubscribeFromLogs = appState.subscribe(message => {
          if (message.type === 'log_message') {
            // Add the log message to our list
            logMessages = [...logMessages, message.data];
            
            // Auto-scroll the log container to the bottom
            setTimeout(() => {
              const logContainer = document.getElementById('log-container');
              if (logContainer) {
                logContainer.scrollTop = logContainer.scrollHeight;
              }
            }, 0);
          } else if (message.type === 'collection_downloaded' && 
                     message.data.type === type && 
                     message.data.name === name) {
            // Download complete
            if (message.data.success) {
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
          <button class="close-button" on:click={closeLogger}>×</button>
        </div>
        <div id="log-container" class="logger-content">
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
  
  .log-timestamp {
    font-size: 0.8rem;
    color: #777;
    margin-right: 0.5rem;
    min-width: 70px;
  }
  
  .log-text {
    flex-grow: 1;
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