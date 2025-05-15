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
  
  // REAPER related state
  let isReaperInitializing = false;
  let isReaperInitComplete = false;
  let reaperInitLog = [];
  let showReaperInitModal = false;
  let isReaperModalLoading = false;
  let isReinitializingReaper = false;
  
  // Tab state
  let activeTab = 'supercollider'; // supercollider, reaper
  
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
        
        // Handle REAPER initialization responses
        if (message.type === 'reaper_init_log') {
          reaperInitLog = [...reaperInitLog, message.data];
          
          // Check for completion flags
          if (message.data.complete) {
            isReaperInitializing = false;
            isReaperInitComplete = true;
            isReaperModalLoading = false;
          }
          
          // Check for user confirmation requests
          if (message.data.confirmation_request) {
            // When an action requires user confirmation, enable the confirm button
            isReaperModalLoading = false;
          }
        }
        
        // Handle REAPER config reset responses
        if (message.type === 'reaper_reinit_result') {
          isReinitializingReaper = false;
          
          if (message.data.success) {
            successMessage = 'REAPER configuration has been reset successfully';
          } else {
            error = message.data.message || 'Failed to reset REAPER configuration';
          }
          
          setTimeout(() => { 
            successMessage = '';
            error = null;
          }, 5000);
        }
        
        // Handle REAPER user directory responses
        if (message.type === 'reaper_user_dir_result') {
          if (!message.data.success) {
            error = message.data.message || 'Failed to open REAPER user directory';
            setTimeout(() => { error = null; }, 5000);
          }
        }
        
        // Handle errors
        if (message.type === 'error') {
          error = message.message;
          isReaperModalLoading = false;
          isReaperInitializing = false;
          isReinitializingReaper = false;
          setTimeout(() => { error = null; }, 5000);
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
  
  // REAPER related functions
  function startReaperInitialization() {
    showReaperInitModal = true;
    reaperInitLog = [];
    isReaperInitComplete = false;
    
    // Start REAPER initialization process
    sendMessage({
      type: 'start_reaper_initialization'
    });
  }
  
  function confirmReaperAction() {
    isReaperModalLoading = true;
    
    sendMessage({
      type: 'confirm_reaper_action'
    });
  }
  
  function closeReaperInitModal() {
    showReaperInitModal = false;
    reaperInitLog = [];
    isReaperInitComplete = false;
  }
  
  function openReaperUserDir() {
    sendMessage({
      type: 'open_reaper_user_dir'
    });
  }
  
  function reinitializeReaper() {
    // Confirm with the user before resetting REAPER config
    if (confirm('This will backup your current REAPER configuration and create a fresh one. Continue?')) {
      isReinitializingReaper = true;
      
      sendMessage({
        type: 'reinit_reaper_with_backup'
      });
      
      // The response will be handled in the subscription
    }
  }
</script>

<div class="container mx-auto px-4 py-8 max-w-6xl">
  <div class="text-center mb-8">
    <h1 class="text-3xl font-bold mb-2 title-font">Audio Backends</h1>
    <p class="text-base-content/70">
      Manage the audio backend systems for Renardo. Different backends enable different sound generation capabilities.
    </p>
  </div>

  <!-- Tab navigation -->
  <div class="tabs tabs-boxed mb-6">
    <button 
      class="tab {activeTab === 'supercollider' ? 'tab-active' : ''}" 
      on:click={() => activeTab = 'supercollider'}>
      SuperCollider
    </button>
    <button 
      class="tab {activeTab === 'reaper' ? 'tab-active' : ''}" 
      on:click={() => activeTab = 'reaper'}>
      REAPER
    </button>
  </div>

  <!-- SuperCollider Backend Tab -->
  {#if activeTab === 'supercollider'}
    <!-- Backend status card -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <div class="flex justify-between items-center mb-4">
          <h2 class="card-title">SuperCollider Backend Status</h2>
          {#if isScBackendRunning}
            <div class="badge badge-success gap-2">
              <span class="relative flex h-3 w-3">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
                <span class="relative inline-flex rounded-full h-3 w-3 bg-success"></span>
              </span>
              Running
            </div>
          {:else}
            <div class="badge badge-error gap-2">
              <span class="relative flex h-3 w-3">
                <span class="relative inline-flex rounded-full h-3 w-3 bg-error"></span>
              </span>
              Stopped
            </div>
          {/if}
        </div>

        <div class="flex flex-wrap gap-2">
          <button
            class="btn btn-primary"
            on:click={startScBackend}
            disabled={isLoading || isScBackendRunning || !$appState.connected}
          >
            {#if isLoading && !isScBackendRunning}
              <span class="loading loading-spinner loading-xs"></span>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
              </svg>
            {/if}
            Start SuperCollider Backend
          </button>

          <button
            class="btn btn-error"
            on:click={stopScBackend}
            disabled={isLoading || !isScBackendRunning || !$appState.connected}
          >
            {#if isLoading && isScBackendRunning}
              <span class="loading loading-spinner loading-xs"></span>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd" />
              </svg>
            {/if}
            Stop SuperCollider Backend
          </button>

          <button
            class="btn btn-outline"
            on:click={checkBackendStatus}
            disabled={isLoading || !$appState.connected}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
            Refresh Status
          </button>
        </div>
      </div>
    </div>

    <!-- Custom initialization code card -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <h2 class="card-title">Initialization Code</h2>
        <p class="text-base-content/70 mb-4">
          Customize the code that will be executed when starting the SuperCollider backend.
          Default code includes starting Renardo and enabling MIDI support.
          <span class="label-text-alt">Default code: <code class="bg-base-300 p-1 rounded text-xs">Renardo.start; Renardo.midi;</code></span>
        </p>
        
        <div class="form-control">
          <label for="sclangCode" class="form-control w-full">
            <textarea
              id="sclangCode"
              class="textarea textarea-bordered font-mono h-32 w-full"
              bind:value={customSclangCode}
              placeholder="Enter SuperCollider initialization code..."
              disabled={isScBackendRunning || isLoading}
            ></textarea>
          </label>
        </div>
      </div>
    </div>

    <!-- Log output card -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <h2 class="card-title">SuperCollider Log Output</h2>

        <div class="bg-base-300 rounded-lg p-4 h-[300px] overflow-y-auto font-mono text-sm">
          {#if logMessages.length === 0 || !logMessages.some(msg => msg.message.includes('SC') || msg.message.includes('SuperCollider') || msg.message.includes('sclang'))}
            <div class="flex justify-center items-center h-full">
              <p class="opacity-50 italic">No log messages yet. Start the SuperCollider backend to see output.</p>
            </div>
          {:else}
            {#each logMessages.filter(msg => msg.message.includes('SC') || msg.message.includes('SuperCollider') || msg.message.includes('sclang')) as log}
              <div class="mb-1 {log.level.toLowerCase() === 'error' ? 'text-error' : log.level.toLowerCase() === 'warn' ? 'text-warning' : log.level.toLowerCase() === 'success' ? 'text-success' : 'text-info'}">
                <span class="opacity-70 mr-2">[{log.timestamp}]</span>
                <span class="font-bold mr-2">[{log.level}]</span>
                <span>{log.message}</span>
              </div>
            {/each}
          {/if}
        </div>
      </div>
    </div>
  {/if}

  <!-- REAPER Backend Tab -->
  {#if activeTab === 'reaper'}
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <h2 class="card-title">REAPER DAW Integration</h2>
        <p class="text-base-content/70 mb-4">
          Integrate Renardo with REAPER Digital Audio Workstation for enhanced audio production capabilities.
          This integration allows Renardo to control REAPER via the ReaPy Python library.
        </p>
        
        <div class="alert alert-info mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span>REAPER must be installed on your system to use this integration. Visit <a href="https://www.reaper.fm/" target="_blank" class="link link-primary">reaper.fm</a> to download.</span>
        </div>
        
        <div class="flex flex-wrap gap-2">
          <button
            class="btn btn-primary"
            on:click={startReaperInitialization}
            disabled={isReaperInitializing || !$appState.connected}
          >
            {#if isReaperInitializing}
              <span class="loading loading-spinner loading-xs"></span>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
              </svg>
            {/if}
            Initialize REAPER Integration
          </button>
          
          <button
            class="btn btn-outline"
            on:click={openReaperUserDir}
            disabled={!$appState.connected}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H8a3 3 0 00-3 3v1.5a1.5 1.5 0 01-3 0V6z" clip-rule="evenodd" />
              <path d="M6 12a2 2 0 012-2h8a2 2 0 012 2v2a2 2 0 01-2 2H2h2a2 2 0 002-2v-2z" />
            </svg>
            Open REAPER User Directory
          </button>
          
          <button
            class="btn btn-warning"
            on:click={reinitializeReaper}
            disabled={isReinitializingReaper || !$appState.connected}
          >
            {#if isReinitializingReaper}
              <span class="loading loading-spinner loading-xs"></span>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
              </svg>
            {/if}
            Reset REAPER Configuration
          </button>
        </div>
      </div>
    </div>
    
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <h2 class="card-title">REAPER Integration Features</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 my-4">
          <div class="border border-base-300 rounded-lg p-4">
            <h3 class="font-bold mb-2">Python-REAPER Bridge</h3>
            <p class="text-base-content/70">
              Control REAPER directly from Renardo using Python code, enabling advanced sequencing and automation.
            </p>
          </div>
          
          <div class="border border-base-300 rounded-lg p-4">
            <h3 class="font-bold mb-2">Cross-Platform Support</h3>
            <p class="text-base-content/70">
              Works on Windows, macOS, and Linux systems with platform-specific optimizations.
            </p>
          </div>
          
          <div class="border border-base-300 rounded-lg p-4">
            <h3 class="font-bold mb-2">DAW Integration</h3>
            <p class="text-base-content/70">
              Leverage REAPER's professional mixing and mastering capabilities alongside Renardo's live coding features.
            </p>
          </div>
          
          <div class="border border-base-300 rounded-lg p-4">
            <h3 class="font-bold mb-2">Project Management</h3>
            <p class="text-base-content/70">
              Create, save, and manage REAPER projects directly from Renardo's interface.
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Log output for REAPER -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <h2 class="card-title">REAPER Integration Log</h2>

        <div class="bg-base-300 rounded-lg p-4 h-[300px] overflow-y-auto font-mono text-sm">
          {#if logMessages.length === 0 || !logMessages.some(msg => msg.message.includes('REAPER') || msg.message.includes('reapy'))}
            <div class="flex justify-center items-center h-full">
              <p class="opacity-50 italic">No REAPER integration logs yet. Initialize REAPER integration to see output.</p>
            </div>
          {:else}
            {#each logMessages.filter(msg => msg.message.includes('REAPER') || msg.message.includes('reapy')) as log}
              <div class="mb-1 {log.level.toLowerCase() === 'error' ? 'text-error' : log.level.toLowerCase() === 'warn' ? 'text-warning' : log.level.toLowerCase() === 'success' ? 'text-success' : 'text-info'}">
                <span class="opacity-70 mr-2">[{log.timestamp}]</span>
                <span class="font-bold mr-2">[{log.level}]</span>
                <span>{log.message}</span>
              </div>
            {/each}
          {/if}
        </div>
      </div>
    </div>
  {/if}

  <!-- Status messages -->
  {#if successMessage}
    <div class="alert alert-success mb-4" transition:fade={{ duration: 300 }}>
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
      <span>{successMessage}</span>
    </div>
  {/if}

  {#if error}
    <div class="alert alert-error mb-4" transition:fade={{ duration: 300 }}>
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
      <span>{error}</span>
    </div>
  {/if}
</div>

<!-- REAPER Initialization Modal -->
{#if showReaperInitModal}
  <div class="modal modal-open">
    <div class="modal-box max-w-2xl">
      <h3 class="font-bold text-lg mb-4">REAPER Integration Setup</h3>
      
      <div class="p-4 bg-base-300 rounded-md mb-4 h-[300px] overflow-y-auto font-mono text-sm">
        {#if reaperInitLog.length === 0}
          <div class="flex justify-center items-center h-full">
            <span class="loading loading-spinner loading-md"></span>
            <p class="ml-2">Initializing REAPER integration...</p>
          </div>
        {:else}
          {#each reaperInitLog as logItem}
            <div class="mb-2">
              <span class={logItem.level === 'ERROR' ? 'text-error' : logItem.level === 'WARN' ? 'text-warning' : logItem.level === 'SUCCESS' ? 'text-success' : 'text-info'}>
                {logItem.message}
              </span>
            </div>
          {/each}
        {/if}
      </div>
      
      <div class="modal-action">
        {#if isReaperInitComplete}
          <button class="btn btn-primary" on:click={closeReaperInitModal}>
            Close
          </button>
        {:else if reaperInitLog.some(log => log.confirmation_request)}
          <button 
            class="btn btn-primary" 
            on:click={confirmReaperAction}
            disabled={isReaperModalLoading}>
            {#if isReaperModalLoading}
              <span class="loading loading-spinner loading-xs"></span>
            {/if}
            Continue
          </button>
        {:else}
          <button class="btn" on:click={closeReaperInitModal}>
            Cancel
          </button>
        {/if}
      </div>
    </div>
  </div>
{/if}