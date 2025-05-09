<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade } from 'svelte/transition';
  import { appState, sendMessage } from './lib/websocket.js';
  
  // Local state
  let isLoading = false;
  let error = null;
  let successMessage = '';
  let logMessages = [];
  let isScBackendRunning = false;
  let customSclangCode = 'Renardo.start; Renardo.midi;'; // Default code
  
  // Subscribe to app state changes
  let unsubscribe;
  
  onMount(() => {
    // Subscribe to appState changes
    unsubscribe = appState.subscribe(state => {
      // Update log messages from application state
      logMessages = state.logMessages || [];
      
      // Check for SC backend running status if available
      if (state.runtimeStatus && state.runtimeStatus.scBackendRunning !== undefined) {
        isScBackendRunning = state.runtimeStatus.scBackendRunning;
      }
      
      // Check for last message for handling specific responses
      if (state._lastMessage) {
        const message = state._lastMessage;
        
        // Handle SC backend startup response
        if (message.type === 'sc_backend_status') {
          isScBackendRunning = message.data.running;
          if (message.data.running) {
            successMessage = 'SuperCollider backend started successfully';
            setTimeout(() => { successMessage = ''; }, 3000);
          }
        }
      }
    });
    
    // Request backend status when component mounts
    checkBackendStatus();
  });
  
  onDestroy(() => {
    // Clean up subscription
    if (unsubscribe) {
      unsubscribe();
    }
  });
  
  // Start SuperCollider backend
  function startScBackend() {
    isLoading = true;
    error = null;
    successMessage = '';
    
    sendMessage({
      type: 'start_sc_backend',
      data: {
        customCode: customSclangCode
      }
    });
    
    // We'll get the response via WebSocket in the subscription
  }
  
  // Check SuperCollider backend status
  function checkBackendStatus() {
    sendMessage({
      type: 'get_sc_backend_status'
    });
  }
  
  // Stop SuperCollider backend
  function stopScBackend() {
    isLoading = true;
    error = null;
    
    sendMessage({
      type: 'stop_sc_backend'
    });
    
    // We'll get the response via WebSocket in the subscription
  }
</script>

<main>
  <div class="container">
    <h1>SuperCollider Backend</h1>
    
    <p class="description">
      Manage the SuperCollider backend for sound synthesis. This backend is required for producing sounds in Renardo.
    </p>
    
    <!-- Backend status -->
    <div class="status-section">
      <div class="status-header">
        <h2>SuperCollider Backend Status</h2>
        <div class="status-indicator {isScBackendRunning ? 'status-running' : 'status-stopped'}">
          {isScBackendRunning ? 'Running' : 'Stopped'}
        </div>
      </div>
      
      <div class="status-actions">
        <button 
          class="primary-button" 
          on:click={startScBackend} 
          disabled={isLoading || isScBackendRunning || !$appState.connected}
        >
          <span class="button-icon">▶️</span> Start SuperCollider Backend
        </button>
        
        <button 
          class="stop-button" 
          on:click={stopScBackend} 
          disabled={isLoading || !isScBackendRunning || !$appState.connected}
        >
          <span class="button-icon">⏹️</span> Stop SuperCollider Backend
        </button>
        
        <button 
          class="refresh-button" 
          on:click={checkBackendStatus} 
          disabled={isLoading || !$appState.connected}
        >
          <span class="button-icon">🔄</span> Refresh Status
        </button>
      </div>
    </div>
    
    <!-- Custom initialization code -->
    <div class="code-section">
      <h2>Initialization Code</h2>
      <p class="description">
        Customize the code that will be executed when starting the SuperCollider backend.
        Default code includes starting Renardo and enabling MIDI support.
      </p>
      
      <div class="code-editor">
        <textarea 
          bind:value={customSclangCode} 
          placeholder="Enter SuperCollider initialization code..." 
          disabled={isScBackendRunning || isLoading}
        ></textarea>
      </div>
      
      <div class="code-info">
        <p>Default code: <code>Renardo.start; Renardo.midi;</code></p>
      </div>
    </div>
    
    <!-- Log output -->
    <div class="log-section">
      <h2>SuperCollider Log Output</h2>
      <div class="log-container">
        {#if logMessages.length === 0}
          <p class="empty-log">No log messages yet. Start the SuperCollider backend to see output.</p>
        {:else}
          {#each logMessages.filter(msg => msg.message.includes('SC') || msg.message.includes('SuperCollider') || msg.message.includes('sclang')) as log}
            <div class="log-entry log-level-{log.level.toLowerCase()}">
              <span class="log-timestamp">[{log.timestamp}]</span>
              <span class="log-level">[{log.level}]</span>
              <span class="log-message">{log.message}</span>
            </div>
          {/each}
        {/if}
      </div>
    </div>
    
    <!-- Status messages -->
    {#if successMessage}
      <div class="success-message" transition:fade={{ duration: 300 }}>
        <p>{successMessage}</p>
      </div>
    {/if}
    
    {#if error}
      <div class="error-message" transition:fade={{ duration: 300 }}>
        <p>{error}</p>
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
    padding: 2rem 0;
  }
  
  .container {
    max-width: 1000px;
    width: 100%;
    padding: 2rem;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  h1 {
    text-align: center;
    margin-top: 0;
    color: #2c3e50;
  }
  
  h2 {
    color: #2c3e50;
    margin-bottom: 0.5rem;
  }
  
  .description {
    color: #7f8c8d;
    margin-bottom: 2rem;
  }
  
  /* Status section */
  .status-section {
    margin-bottom: 2rem;
    padding: 1.25rem;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    background-color: #fafafa;
  }
  
  .status-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  
  .status-header h2 {
    margin: 0;
  }
  
  .status-indicator {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
  }
  
  .status-running {
    background-color: #e8f5e9;
    color: #2e7d32;
  }
  
  .status-stopped {
    background-color: #ffebee;
    color: #c62828;
  }
  
  .status-actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }
  
  /* Code section */
  .code-section {
    margin-bottom: 2rem;
    padding: 1.25rem;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    background-color: #fafafa;
  }
  
  .code-editor {
    margin-bottom: 1rem;
  }
  
  textarea {
    width: 100%;
    min-height: 120px;
    padding: 0.75rem;
    font-family: 'Fira Code', Consolas, monospace;
    font-size: 0.9rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: vertical;
  }
  
  textarea:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }
  
  .code-info {
    color: #666;
    font-size: 0.9rem;
  }
  
  .code-info code {
    background-color: #f0f0f0;
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-size: 0.85rem;
  }
  
  /* Log section */
  .log-section {
    margin-bottom: 2rem;
  }
  
  .log-container {
    height: 300px;
    overflow-y: auto;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: #f8f9fa;
    font-family: 'Fira Code', Consolas, monospace;
    font-size: 0.9rem;
  }
  
  .log-entry {
    margin-bottom: 0.25rem;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-word;
  }
  
  .log-timestamp {
    color: #666;
    margin-right: 0.5rem;
  }
  
  .log-level {
    font-weight: 500;
    margin-right: 0.5rem;
  }
  
  .log-level-info {
    color: #2196f3;
  }
  
  .log-level-warn {
    color: #ff9800;
  }
  
  .log-level-error {
    color: #f44336;
  }
  
  .log-level-success {
    color: #4caf50;
  }
  
  .empty-log {
    color: #999;
    text-align: center;
    padding: 1rem 0;
  }
  
  /* Buttons */
  button {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .primary-button {
    background-color: #3498db;
    color: white;
  }
  
  .primary-button:hover:not(:disabled) {
    background-color: #2980b9;
  }
  
  .stop-button {
    background-color: #e74c3c;
    color: white;
  }
  
  .stop-button:hover:not(:disabled) {
    background-color: #c0392b;
  }
  
  .refresh-button {
    background-color: #95a5a6;
    color: white;
  }
  
  .refresh-button:hover:not(:disabled) {
    background-color: #7f8c8d;
  }
  
  .button-icon {
    margin-right: 0.5rem;
  }
  
  /* Status messages */
  .success-message {
    background-color: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 4px;
    margin-top: 1rem;
  }
  
  .error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 4px;
    margin-top: 1rem;
  }
  
  /* Responsive layout */
  @media (max-width: 768px) {
    .status-actions {
      flex-direction: column;
    }
    
    button {
      width: 100%;
    }
  }
</style>