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

<div class="container mx-auto px-4 py-8 max-w-4xl">
  <div class="text-center mb-8">
    <h1 class="text-3xl font-bold mb-2 title-font">SuperCollider Backend</h1>
    <p class="text-base-content/70">
      Manage the SuperCollider backend for sound synthesis. This backend is required for producing sounds in Renardo.
    </p>
  </div>

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