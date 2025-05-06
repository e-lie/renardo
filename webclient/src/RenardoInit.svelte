<script>
  import { onMount } from 'svelte';
  import { appState, initWebSocket, sendMessage } from './lib/websocket.js';
  
  // Local state for initialization status
  let scFilesInitialized = false;
  let samplesInitialized = false;
  let instrumentsInitialized = false;
  
  // Runtime status
  let scBackendRunning = false;
  let renardoRuntimeRunning = false;
  
  // Log messages collection
  let logMessages = [];
  
  // Reference to log container for autoscrolling
  let logContainer;
  
  // Check if WebSockets are supported
  const webSocketSupported = 'WebSocket' in window;
  
  // Function to scroll log container to bottom
  function scrollToBottom() {
    if (logContainer) {
      setTimeout(() => {
        logContainer.scrollTop = logContainer.scrollHeight;
      }, 50);
    }
  }
  
  // Initialize WebSocket connection on mount
  onMount(() => {
    if (webSocketSupported) {
      initWebSocket();
      
      // Subscribe to appState changes
      const unsubscribe = appState.subscribe(state => {
        if (state.renardoInit) {
          scFilesInitialized = state.renardoInit.superColliderClasses;
          samplesInitialized = state.renardoInit.samples;
          instrumentsInitialized = state.renardoInit.instruments;
        }
        
        if (state.runtimeStatus) {
          scBackendRunning = state.runtimeStatus.scBackendRunning;
          renardoRuntimeRunning = state.runtimeStatus.renardoRuntimeRunning;
        }
        
        if (state.logMessages && state.logMessages.length > 0) {
          const prevLogCount = logMessages.length;
          logMessages = state.logMessages;
          
          // If new log messages were added, scroll to bottom
          if (logMessages.length > prevLogCount) {
            scrollToBottom();
          }
        }
      });
      
      // Clean up subscription on component unmount
      return () => {
        unsubscribe();
      };
    }
  });
  
  // Initialization functions
  function initSuperColliderClasses() {
    // Reset any previous error
    appState.update(state => ({
      ...state,
      error: null
    }));
    
    return sendMessage({
      type: 'init_supercollider_classes'
    });
  }
  
  function downloadSamples() {
    // Reset any previous error
    appState.update(state => ({
      ...state,
      error: null
    }));
    
    return sendMessage({
      type: 'download_samples'
    });
  }
  
  function downloadInstruments() {
    // Reset any previous error
    appState.update(state => ({
      ...state,
      error: null
    }));
    
    return sendMessage({
      type: 'download_instruments'
    });
  }
  
  // Runtime functions
  function startSuperColliderBackend() {
    // Reset any previous error
    appState.update(state => ({
      ...state,
      error: null
    }));
    
    return sendMessage({
      type: 'start_supercollider_backend'
    });
  }
  
  function startRenardoRuntime() {
    // Reset any previous error
    appState.update(state => ({
      ...state,
      error: null
    }));
    
    return sendMessage({
      type: 'start_renardo_runtime'
    });
  }
  
  // Helper function to get status class
  function getStatusClass(status) {
    return status ? 'status-success' : 'status-pending';
  }
  
  // Helper function to navigate to editor
  function goToEditor() {
    window.location.hash = '#editor';
  }
</script>

<main>
  <div class="container">
    <h1>Renardo Initialization</h1>
    
    <!-- Connection status -->
    <div class="status-bar">
      {#if webSocketSupported}
        <div class="status-indicator" class:connected={$appState.connected}>
          {$appState.connected ? 'Connected' : 'Disconnected'}
        </div>
      {:else}
        <div class="status-indicator fallback">
          Using HTTP Fallback (WebSockets not supported)
        </div>
      {/if}
    </div>
    
    <p class="description">
      Initialize Renardo components before starting to make music. 
      Each component must be initialized in order.
    </p>
    
    <!-- Initialization buttons -->
    <div class="init-section">
      <div class="init-item">
        <div class="init-header">
          <h3>1. Initialize SuperCollider Classes</h3>
          <div class="status-badge {getStatusClass(scFilesInitialized)}">
            {scFilesInitialized ? 'Initialized' : 'Pending'}
          </div>
        </div>
        <p>Sets up SuperCollider configuration in your user directory.</p>
        <button 
          on:click={initSuperColliderClasses} 
          disabled={!$appState.connected || scFilesInitialized}
        >
          Initialize SuperCollider
        </button>
      </div>
      
      <div class="init-item">
        <div class="init-header">
          <h3>2. Download Sample Packs</h3>
          <div class="status-badge {getStatusClass(samplesInitialized)}">
            {samplesInitialized ? 'Downloaded' : 'Pending'}
          </div>
        </div>
        <p>Downloads sound samples for your compositions.</p>
        <button 
          on:click={downloadSamples} 
          disabled={!$appState.connected || samplesInitialized || !scFilesInitialized}
        >
          Download Samples
        </button>
      </div>
      
      <div class="init-item">
        <div class="init-header">
          <h3>3. Download Instruments &amp; Effects</h3>
          <div class="status-badge {getStatusClass(instrumentsInitialized)}">
            {instrumentsInitialized ? 'Downloaded' : 'Pending'}
          </div>
        </div>
        <p>Downloads instruments and effects for your compositions.</p>
        <button 
          on:click={downloadInstruments} 
          disabled={!$appState.connected || instrumentsInitialized || !samplesInitialized}
        >
          Download Instruments
        </button>
      </div>
    </div>
    
    <!-- Runtime buttons -->
    <div class="runtime-section">
      <h2>Launch Renardo</h2>
      <p class="description">Start the SuperCollider backend and Renardo runtime</p>
      
      <div class="runtime-controls">
        <div class="runtime-item">
          <div class="runtime-header">
            <h3>1. Start SuperCollider Backend</h3>
            <div class="status-badge {getStatusClass(scBackendRunning)}">
              {scBackendRunning ? 'Running' : 'Stopped'}
            </div>
          </div>
          <p>Starts the SuperCollider server that processes audio.</p>
          <button 
            on:click={startSuperColliderBackend} 
            disabled={!$appState.connected || !scFilesInitialized || scBackendRunning}
          >
            Launch SuperCollider
          </button>
        </div>
        
        <div class="runtime-item">
          <div class="runtime-header">
            <h3>2. Start Renardo Runtime</h3>
            <div class="status-badge {getStatusClass(renardoRuntimeRunning)}">
              {renardoRuntimeRunning ? 'Running' : 'Stopped'}
            </div>
          </div>
          <p>Initializes the Renardo runtime environment.</p>
          <button 
            on:click={startRenardoRuntime} 
            disabled={!$appState.connected || !scBackendRunning || renardoRuntimeRunning}
          >
            Launch Renardo
          </button>
        </div>
      </div>
      
      <!-- Go to editor button -->
      <div class="editor-link">
        <button 
          on:click={goToEditor} 
          disabled={!renardoRuntimeRunning}
          class="editor-button"
        >
          Open Code Editor
        </button>
      </div>
    </div>
    
    <!-- Log output -->
    <div class="log-section">
      <h3>Initialization Log</h3>
      <div class="log-container" bind:this={logContainer}>
        {#if logMessages.length === 0}
          <p class="log-empty">No log messages yet. Start initialization to see progress.</p>
        {:else}
          {#each logMessages as log}
            <div class="log-entry log-level-{log.level.toLowerCase()}">
              <span class="log-timestamp">[{log.timestamp}]</span>
              <span class="log-message">{log.message}</span>
            </div>
          {/each}
        {/if}
      </div>
    </div>
    
    <!-- Success message when all components are initialized -->
    {#if scFilesInitialized && samplesInitialized && instrumentsInitialized}
      <div class="success-message">
        <h3>🎉 All components initialized successfully!</h3>
        <p>You're ready to start making music with Renardo.</p>
      </div>
    {/if}
    
    <!-- Error messages -->
    {#if $appState.error}
      <div class="error-message">
        Error: {$appState.error}
      </div>
    {/if}
  </div>
</main>

<style>
  main {
    width: 100%;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem 0;
  }
  
  .container {
    max-width: 800px;
    width: 100%;
    padding: 2rem;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  h1, h2 {
    text-align: center;
    margin-top: 0;
    color: #2c3e50;
  }
  
  h2 {
    margin-top: 2rem;
    margin-bottom: 0.5rem;
  }
  
  .status-bar {
    display: flex;
    justify-content: center;
    margin-bottom: 1rem;
  }
  
  .status-indicator {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
    background-color: #f44336;
    color: white;
  }
  
  .status-indicator.connected {
    background-color: #4caf50;
  }
  
  .status-indicator.fallback {
    background-color: #ff9800;
  }
  
  .description {
    text-align: center;
    margin-bottom: 2rem;
    color: #7f8c8d;
  }
  
  .init-section, .runtime-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .runtime-section {
    border-top: 1px solid #e0e0e0;
    padding-top: 1.5rem;
  }
  
  .runtime-controls {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .init-item, .runtime-item {
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 1.25rem;
    background-color: #fafafa;
  }
  
  .init-header, .runtime-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  
  .init-header h3, .runtime-header h3 {
    margin: 0;
    color: #2c3e50;
  }
  
  .status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .status-pending {
    background-color: #f5f5f5;
    color: #757575;
  }
  
  .status-success {
    background-color: #e8f5e9;
    color: #2e7d32;
  }
  
  button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
    margin-top: 0.5rem;
  }
  
  button:hover:not(:disabled) {
    background-color: #2980b9;
  }
  
  button:active:not(:disabled) {
    transform: translateY(1px);
  }
  
  button:disabled {
    background-color: #e0e0e0;
    color: #9e9e9e;
    cursor: not-allowed;
  }
  
  .editor-link {
    display: flex;
    justify-content: center;
    margin-top: 2rem;
  }
  
  .editor-button {
    background-color: #2ecc71;
    font-size: 1.1rem;
    padding: 1rem 2rem;
  }
  
  .editor-button:hover:not(:disabled) {
    background-color: #27ae60;
  }
  
  .log-section {
    margin-top: 2rem;
  }
  
  .log-section h3 {
    margin-bottom: 0.5rem;
  }
  
  .log-container {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 0.5rem;
    background-color: #f5f5f5;
    font-family: monospace;
  }
  
  .log-entry {
    padding: 0.25rem 0;
    border-bottom: 1px solid #eeeeee;
    font-size: 0.9rem;
  }
  
  .log-entry:last-child {
    border-bottom: none;
  }
  
  .log-timestamp {
    color: #757575;
    margin-right: 0.5rem;
  }
  
  .log-level-info {
    color: #1976d2;
  }
  
  .log-level-warn {
    color: #ff9800;
  }
  
  .log-level-error {
    color: #e53935;
  }
  
  .log-level-success {
    color: #43a047;
  }
  
  .log-empty {
    color: #9e9e9e;
    text-align: center;
    font-style: italic;
  }
  
  .success-message {
    margin-top: 2rem;
    padding: 1.5rem;
    background-color: #e8f5e9;
    border-radius: 6px;
    text-align: center;
  }
  
  .success-message h3 {
    margin-top: 0;
    color: #2e7d32;
  }
  
  .success-message p {
    margin-bottom: 1.5rem;
  }
  
  .button {
    background-color: #4caf50;
    color: white;
    text-decoration: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .button:hover {
    background-color: #388e3c;
  }
  
  .error-message {
    background-color: #ffebee;
    color: #c62828;
    padding: 1rem;
    border-radius: 4px;
    margin-top: 1.5rem;
  }
</style>