<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade } from 'svelte/transition';
  import { appState, sendMessage } from './lib/websocket.js';
  
  // Local state
  let isLoading = false;
  let isSCCodeExecuting = false;
  let error = null;
  let successMessage = '';
  let logMessages = [];
  let isScBackendRunning = false;
  let isRenardoInitialized = false;
  let customSclangCode = 'Renardo.start(); Renardo.midi();'; // Default code
  
  
  // REAPER related state
  let isReaperInitializing = false;
  let isReaperInitComplete = false;
  let reaperInitLog = [];
  let showReaperInitModal = false;
  let showReaperResetModal = false;
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
        isRenardoInitialized = state.runtimeStatus.renardoRuntimeRunning || false;
      }
      
      // Check for last message for handling specific responses
      if (state._lastMessage) {
        const message = state._lastMessage;
        
        // Handle SC backend startup response
        if (message.type === 'sc_backend_status') {
          isScBackendRunning = message.data.running;
          if (message.data.renardoInitialized !== undefined) {
            isRenardoInitialized = message.data.renardoInitialized;
          }
          
          if (message.data.running) {
            successMessage = 'SuperCollider backend started successfully';
            setTimeout(() => { successMessage = ''; }, 3000);
          }
        }
        
        // Handle SC code execution response
        if (message.type === 'sc_code_execution_result') {
          isSCCodeExecuting = false;
          
          if (message.data.success) {
            const output = message.data.message || '';
            
            console.log("SuperCollider execution result:", output);
            
            // General success message
            successMessage = message.data.message || 'SuperCollider code executed successfully';
            setTimeout(() => { successMessage = ''; }, 3000);
          }
        }
        
        // Handle SuperCollider IDE launch response
        if (message.type === 'sc_ide_launch_result') {
          if (message.data.success) {
            successMessage = message.data.message || 'SuperCollider IDE launched successfully';
            setTimeout(() => { successMessage = ''; }, 3000);
          } else {
            error = message.data.message || 'Failed to launch SuperCollider IDE';
            setTimeout(() => { error = null; }, 5000);
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
          console.log("Received reaper_reinit_result:", message);
          isReinitializingReaper = false;
          
          // Create a log entry for the reset result
          const resetResultEntry = {
            timestamp: new Date().toLocaleTimeString(),
            level: message.data.success ? 'SUCCESS' : 'ERROR',
            message: message.data.success 
              ? 'REAPER configuration has been reset successfully. A backup of your previous configuration has been created.' 
              : message.data.message || 'Failed to reset REAPER configuration'
          };
          
          // Add this log entry to our log messages
          logMessages = [...logMessages, resetResultEntry];
          
          // Also display a user notification
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
        
        // Handle REAPER launch responses
        if (message.type === 'reaper_launch_result') {
          console.log("Received reaper_launch_result:", message);
          
          // Create a log entry for the launch result
          const launchResultEntry = {
            timestamp: new Date().toLocaleTimeString(),
            level: message.data.success ? 'SUCCESS' : 'ERROR',
            message: message.data.success 
              ? `REAPER launched successfully with PYTHONHOME=${message.data.pythonhome}` 
              : message.data.message || 'Failed to launch REAPER'
          };
          
          // Add this log entry to our log messages
          logMessages = [...logMessages, launchResultEntry];
          
          // Also display a user notification
          if (message.data.success) {
            successMessage = message.data.pythonhome 
              ? `REAPER launched successfully with PYTHONHOME=${message.data.pythonhome}`
              : 'REAPER launched successfully';
          } else {
            error = message.data.message || 'Failed to launch REAPER';
          }
          
          // If we have PYTHONHOME, add a more detailed log entry explaining its importance
          if (message.data.success && message.data.pythonhome) {
            const pythonHomeInfoEntry = {
              timestamp: new Date().toLocaleTimeString(),
              level: 'INFO',
              message: `The PYTHONHOME environment variable is set to point to the Python installation used by Renardo. This ensures REAPER can correctly load Python plugins and extensions.`
            };
            logMessages = [...logMessages, pythonHomeInfoEntry];
          }
          
          setTimeout(() => { 
            successMessage = '';
            error = null;
          }, 8000); // Increase timeout to give users time to read the PYTHONHOME path
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
      type: 'start_sc_backend'
    });
    
    // We'll get the response via WebSocket in the subscription
  }
  
  // Execute Renardo initialization code in SuperCollider
  function executeScCode() {
    isSCCodeExecuting = true;
    error = null;
    successMessage = '';
    
    sendMessage({
      type: 'execute_sc_code',
      data: {
        customCode: customSclangCode
      }
    });
    
    // We'll get the response via WebSocket in the subscription
  }
  
  
  // Launch SuperCollider IDE
  function launchSupercolliderIDE() {
    error = null;
    successMessage = '';
    
    sendMessage({
      type: 'launch_supercollider_ide'
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
  
  function cancelReaperSetup() {
    // Just close the modal and reset state
    showReaperInitModal = false;
    reaperInitLog = [];
    isReaperInitComplete = false;
    isReaperInitializing = false;
    isReaperModalLoading = false;
  }
  
  function openReaperUserDir() {
    sendMessage({
      type: 'open_reaper_user_dir'
    });
  }
  
  function reinitializeReaper() {
    // Show the confirmation modal
    showReaperResetModal = true;
  }
  
  function confirmReaperReset() {
    // User confirmed the reset
    showReaperResetModal = false;
    isReinitializingReaper = true;
    
    // Add a log entry for the reset action
    const resetLogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      level: 'INFO',
      message: 'Resetting REAPER configuration with backup...'
    };
    
    // Manually add to log messages to ensure it's visible immediately
    logMessages = [...logMessages, resetLogEntry];
    
    console.log("Sending reinit_reaper_with_backup message");
    
    // Send the reset command
    sendMessage({
      type: 'reinit_reaper_with_backup'
    });
    
    // The response will be handled in the subscription
  }
  
  function cancelReaperReset() {
    // User canceled the reset
    showReaperResetModal = false;
  }

  function launchReaper() {
    // Add a log entry for launching REAPER
    const launchLogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      level: 'INFO',
      message: 'Launching REAPER with correct PYTHONHOME environment...'
    };
    
    // Manually add to log messages to ensure it's visible immediately
    logMessages = [...logMessages, launchLogEntry];
    
    // Send the launch REAPER command
    sendMessage({
      type: 'launch_reaper_pythonhome'
    });
  }
  
</script>

<div class="container mx-auto px-4 py-8 max-w-6xl">
  <div class="text-center mb-8">
    <h1 class="text-3xl font-bold mb-2 title-font">Audio Backends</h1>
    <p class="text-base-content/70">
      Manage the audio backend systems for Renardo. Each backend offers different capabilities for music creation and production.
    </p>
  </div>

  <!-- Tab navigation -->
  <div class="mb-8">
    <div class="tabs tabs-lg">
      <button 
        class="tab tab-lifted {activeTab === 'supercollider' ? 'tab-active bg-base-200 font-bold' : ''} flex items-center gap-2 px-6" 
        on:click={() => activeTab = 'supercollider'}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
        </svg>
        SuperCollider
      </button>
      <button 
        class="tab tab-lifted {activeTab === 'reaper' ? 'tab-active bg-base-200 font-bold' : ''} flex items-center gap-2 px-6" 
        on:click={() => activeTab = 'reaper'}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd" />
        </svg>
        REAPER
      </button>
    </div>
    <div class="h-1 bg-base-200 -mt-1 mb-4"></div>
  </div>

  <!-- SuperCollider Backend Tab -->
  {#if activeTab === 'supercollider'}
    <div class="bg-base-200 p-4 rounded-lg mb-6">
      <h2 class="text-2xl font-bold mb-2 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
          <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
        </svg>
        SuperCollider Sound Engine
      </h2>
      <p class="text-base-content/70 mb-2">
        SuperCollider is an audio synthesis and algorithmic composition platform. 
        It's the primary sound engine for Renardo's live coding capabilities.
      </p>
    </div>
    <!-- Backend status card -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <div class="flex justify-between items-center mb-4">
          <h2 class="card-title">SuperCollider Backend Status</h2>
          <div class="flex gap-2">
            {#if isScBackendRunning}
              <div class="badge badge-success gap-2">
                <span class="relative flex h-3 w-3">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-3 w-3 bg-success"></span>
                </span>
                SuperCollider Running
              </div>
            {:else}
              <div class="badge badge-error gap-2">
                <span class="relative flex h-3 w-3">
                  <span class="relative inline-flex rounded-full h-3 w-3 bg-error"></span>
                </span>
                SuperCollider Stopped
              </div>
            {/if}
            
            {#if isRenardoInitialized}
              <div class="badge badge-success gap-2">
                <span class="relative flex h-3 w-3">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-3 w-3 bg-success"></span>
                </span>
                Renardo Initialized
              </div>
            {:else if isScBackendRunning}
              <div class="badge badge-warning gap-2">
                <span class="relative flex h-3 w-3">
                  <span class="relative inline-flex rounded-full h-3 w-3 bg-warning"></span>
                </span>
                Not Initialized
              </div>
            {/if}
          </div>
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
    
    <!-- SuperCollider Documentation -->
    <div class="collapse collapse-arrow bg-base-200 shadow-md mb-8">
      <input type="checkbox" /> 
      <div class="collapse-title text-md font-medium">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        SuperCollider troubleshooting and manual setup
      </div>
      <div class="collapse-content bg-base-100"> 
        <div class="prose">
          <p>
            SuperCollider/sclang can behave in unexpected ways depending on your system configuration, audio setup, 
            and other software running. If you encounter issues with automatic initialization, you can start the backend manually:
          </p>
          
          <ol>
            <li>Open SuperCollider (IDE) application</li>
            <li>Execute the following code to start the audio server on the first Audio device:
              <pre class="bg-base-300 p-2 rounded"><code>Renardo.start()</code></pre>
            </li>
            <li>Execute the following code to start the Renardo SuperCollider MIDI on the first MIDI device:
              <pre class="bg-base-300 p-2 rounded"><code>Renardo.midi()</code></pre>
            </li>
          </ol>
          
          <p class="text-sm opacity-75">
            Note: The parameter "0" in these commands refers to the device index. You can use different indices if you have multiple 
            audio or MIDI devices and want to use a specific one.
          </p>
          
          <div class="flex justify-center mt-6">
            <button 
              class="btn btn-primary" 
              on:click={launchSupercolliderIDE}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
              </svg>
              Launch SuperCollider IDE
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Custom initialization code card -->
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <h2 class="card-title">Renardo Initialization Code</h2>
        <p class="text-base-content/70 mb-4">
          Customize the code that will be executed to initialize Renardo in the running SuperCollider instance.
          Default code initializes Renardo without MIDI support.
          <span class="label-text-alt">Default code: <code class="bg-base-300 p-1 rounded text-xs">Renardo.start();  Renardo.midi();</code></span>
        </p>
        
        {#if isRenardoInitialized}
          <div class="alert alert-success mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span>Renardo has been initialized in SuperCollider. You're ready to start coding music!</span>
          </div>
        {:else if isScBackendRunning}
          <div class="alert alert-warning mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            <span>SuperCollider is running but Renardo has not been initialized yet. Click the "Execute Renardo Init Code" button to complete setup.</span>
          </div>
        {/if}
        
        <div class="form-control">
          <label for="sclangCode" class="form-control w-full mb-4">
            <textarea
              id="sclangCode"
              class="textarea textarea-bordered font-mono h-32 w-full"
              bind:value={customSclangCode}
              placeholder="Enter SuperCollider initialization code..."
              disabled={isRenardoInitialized || isSCCodeExecuting}
            ></textarea>
          </label>
          
          <div class="flex justify-end">
            <button
              class="btn btn-success btn-lg"
              on:click={executeScCode}
              disabled={isSCCodeExecuting || !isScBackendRunning || isRenardoInitialized || !$appState.connected}
            >
              {#if isSCCodeExecuting}
                <span class="loading loading-spinner loading-sm"></span>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                </svg>
              {/if}
              Execute Renardo Init Code
            </button>
          </div>
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
    <div class="bg-base-200 p-4 rounded-lg mb-6">
      <h2 class="text-2xl font-bold mb-2 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd" />
        </svg>
        REAPER Digital Audio Workstation
      </h2>
      <p class="text-base-content/70 mb-2">
        REAPER is a classic multiplateform digital audio workstation (DAW). Renardo propose an integration with Reaper to bridge the world of livecoding and classic music production.
      </p>
    </div>
    <div class="card bg-base-100 shadow-xl mb-8">
      <div class="card-body">
        <h2 class="card-title">REAPER DAW Integration</h2>
        <p class="text-base-content/70 mb-4">
          This integration allows Renardo to control REAPER via a fork of the Reapy Python library.
        </p>
        
        <div class="alert alert-info mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span>REAPER must be installed on your system to use this integration. Visit <a href="https://www.reaper.fm/" target="_blank" class="link link-primary">reaper.fm</a> to download.</span>
        </div>
        
        <div class="alert alert-warning mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          <span><strong>Important:</strong> Always launch REAPER through Renardo using the "Launch REAPER" button below. This sets the correct PYTHONHOME environment variable. Launching REAPER directly may cause it to crash when using Python functionality.</span>
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
            class="btn btn-primary"
            on:click={launchReaper}
            disabled={!$appState.connected}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
            </svg>
            Launch REAPER
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
          <button class="btn" on:click={cancelReaperSetup}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Cancel Setup
          </button>
          <button 
            class="btn btn-primary" 
            on:click={confirmReaperAction}
            disabled={isReaperModalLoading}>
            {#if isReaperModalLoading}
              <span class="loading loading-spinner loading-xs"></span>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            {/if}
            Continue
          </button>
        {:else}
          <button class="btn" on:click={cancelReaperSetup}>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Cancel Setup
          </button>
        {/if}
      </div>
    </div>
  </div>
{/if}

<!-- REAPER Reset Configuration Modal -->
{#if showReaperResetModal}
  <div class="modal modal-open">
    <div class="modal-box">
      <h3 class="font-bold text-xl mb-4 text-warning">Reset REAPER Configuration</h3>
      
      <p class="mb-4">
        This action will:
      </p>
      
      <ul class="list-disc list-inside mb-6 space-y-2">
        <li>Back up your current REAPER configuration</li>
        <li>Create a fresh configuration optimized for Renardo</li>
        <li>Overwrite any custom REAPER settings you may have</li>
      </ul>
      
      <div class="alert alert-warning mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
        <span>This action cannot be undone, but a backup will be created automatically.</span>
      </div>
      
      <p class="mb-4 text-sm opacity-70">
        Note: The backup will be saved in your REAPER user directory. You can restore it manually if needed.
      </p>
      
      <div class="modal-action">
        <button class="btn" on:click={cancelReaperReset}>
          Cancel
        </button>
        <button class="btn btn-warning" on:click={confirmReaperReset}>
          {#if isReinitializingReaper}
            <span class="loading loading-spinner loading-xs"></span>
          {/if}
          Reset Configuration
        </button>
      </div>
    </div>
  </div>
{/if}