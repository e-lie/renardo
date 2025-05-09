<script>
  import { onMount } from 'svelte';
  import { appState, initWebSocket, sendMessage } from './lib/websocket.js';
  
  // Local state for initialization status
  let scFilesInitialized = false;
  let samplesInitialized = false;
  let instrumentsInitialized = false;
  let sclangCodeInitialized = false;
  
  // We'll assume websockets are managed by the parent App component
  
  // Initialize component on mount
  onMount(() => {
    // Subscribe to appState changes
    const unsubscribe = appState.subscribe(state => {
      if (state.renardoInit) {
        // Update local state variables from appState
        scFilesInitialized = state.renardoInit.superColliderClasses;
        samplesInitialized = state.renardoInit.samples;
        instrumentsInitialized = state.renardoInit.instruments;
        
        // Handle sclangCode field, which might be missing in older state objects
        sclangCodeInitialized = state.renardoInit.sclangCode === true;
      }
    });
    
    // Force request status after a short delay
    setTimeout(() => {
      if ($appState.connected) {
        sendMessage({
          type: 'get_renardo_status'
        });
      }
    }, 500);
    
    // Clean up subscription on component unmount
    return () => {
      unsubscribe();
    };
  });
  
  // Initialization function for SuperCollider
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
  
  // Initialization function for SCLang Code
  function downloadSclangCode() {
    // Reset any previous error
    appState.update(state => ({
      ...state,
      error: null
    }));
    
    return sendMessage({
      type: 'download_sclang_code'
    });
  }
  
  // Helper function to get status class
  function getStatusClass(status) {
    return status ? 'status-success' : 'status-pending';
  }
  
  // Navigate to collections
  function goToCollections() {
    window.location.hash = '#collections';
  }
</script>

<main>
  <div class="container">
    <h1>Renardo Initialization</h1>
    
    <p class="description">
      Initialize Renardo components before starting to make music.
    </p>
    
    <!-- Initialization section -->
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
          <h3>2. Download SCLang Code</h3>
          <div class="status-badge {getStatusClass(sclangCodeInitialized)}">
            {sclangCodeInitialized ? 'Downloaded' : 'Not Installed'}
          </div>
        </div>
        <p>Required SuperCollider language code for special features.</p>
        {#if !sclangCodeInitialized}
          <button 
            class="secondary-button" 
            on:click={downloadSclangCode}
            disabled={!$appState.connected || sclangCodeInitialized}
          >
            <span class="button-icon">📄</span> Download SuperCollider Language Code
          </button>
        {/if}
      </div>
      
      <div class="init-item">
        <div class="init-header">
          <h3>3. Sample Packs</h3>
          <div class="status-badge {getStatusClass(samplesInitialized)}">
            {samplesInitialized ? 'Downloaded' : 'Not Installed'}
          </div>
        </div>
        <p>Sound samples for your compositions.</p>
        {#if !samplesInitialized}
          <button class="secondary-button" on:click={goToCollections}>
            <span class="button-icon">📦</span> Download Default Sample Pack (0_foxdot_default)
          </button>
        {/if}
      </div>
      
      <div class="init-item">
        <div class="init-header">
          <h3>4. Instruments &amp; Effects</h3>
          <div class="status-badge {getStatusClass(instrumentsInitialized)}">
            {instrumentsInitialized ? 'Downloaded' : 'Not Installed'}
          </div>
        </div>
        <p>Instruments and effects for your compositions.</p>
        {#if !instrumentsInitialized}
          <button class="secondary-button" on:click={goToCollections}>
            <span class="button-icon">🎹</span> Download Default Instruments & Effects
          </button>
        {/if}
      </div>
    </div>
    
    <!-- Success message when all components are initialized -->
    {#if scFilesInitialized && sclangCodeInitialized && samplesInitialized && instrumentsInitialized}
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
  
  h1{
    text-align: center;
    margin-top: 0;
    color: #2c3e50;
  }
  
  
  .description {
    text-align: center;
    margin-bottom: 2rem;
    color: #7f8c8d;
  }
  
  .init-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .init-item {
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 1.25rem;
    background-color: #fafafa;
  }
  
  .init-header{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  
  .init-header h3{
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
  
  .secondary-button {
    background-color: #2ecc71;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
    margin-top: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
  }
  
  .secondary-button:hover {
    background-color: #27ae60;
  }
  
  .secondary-button:active {
    transform: translateY(1px);
  }
  
  .button-icon {
    margin-right: 0.5rem;
    font-size: 1.2rem;
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
    margin-bottom: 0;
  }
  
  .error-message {
    background-color: #ffebee;
    color: #c62828;
    padding: 1rem;
    border-radius: 4px;
    margin-top: 1.5rem;
  }
</style>