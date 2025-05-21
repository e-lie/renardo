<script>
  import { onMount } from 'svelte';
  import { appState, initWebSocket, sendMessage } from './lib/websocket.js';
  import ThemeSelector from './lib/ThemeSelector.svelte';

  // Local state for initialization status
  let scFilesInitialized = false;
  let samplesInitialized = false;
  let instrumentsInitialized = false;
  let sclangCodeInitialized = false;
  let reaperPackInitialized = false;

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
        
        // Handle reaperPack field
        reaperPackInitialized = state.renardoInit.reaperPack === true;
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

  // Initialization function for Reaper Default Pack
  function initReaperDefaultPack() {
    // Reset any previous error
    appState.update(state => ({
      ...state,
      error: null
    }));

    // Use fetch instead of websocket for this operation
    return fetch('/api/reaper/initialize_default_pack', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Update app state
        appState.update(state => ({
          ...state,
          renardoInit: {
            ...state.renardoInit,
            reaperPack: true
          }
        }));
      } else {
        // Show error
        appState.update(state => ({
          ...state,
          error: data.message || 'Failed to initialize Reaper default pack'
        }));
      }
      return data;
    })
    .catch(error => {
      console.error('Error initializing Reaper default pack:', error);
      appState.update(state => ({
        ...state,
        error: 'Error initializing Reaper default pack'
      }));
    });
  }

  // Navigation functions
  function goToCollections() {
    window.location.hash = '#collections';
  }

  function navigate(route) {
    window.location.hash = `#${route}`;
  }
</script>

<div class="container mx-auto px-4 py-8 max-w-6xl">
  <div class="text-center mb-8">
    <h1 class="text-3xl font-bold mb-2 title-font">Renardo Initialization</h1>
    <p class="text-base-content/70">
      Initialize Renardo components before starting to make music.
    </p>
  </div>

  <!-- Progress Overview Card -->
  <div class="card bg-base-100 shadow-xl mb-8">
    <div class="card-body">
      <h2 class="card-title title-font">Initialization Progress >></h2>
      <div class="flex flex-col md:flex-row items-center gap-6 mb-4">
        <div class="stats shadow flex-1">
          <div class="stat">
            <div class="stat-figure text-primary">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25" />
              </svg>
            </div>
            <div class="stat-title">Components Ready</div>
            <div class="stat-value text-primary">{[scFilesInitialized, sclangCodeInitialized, samplesInitialized, instrumentsInitialized, reaperPackInitialized].filter(Boolean).length}/5</div>
            <div class="stat-desc">Components initialized and ready to use</div>
          </div>
        </div>
      </div>

      <!-- Success message when all components are initialized -->
      {#if scFilesInitialized && sclangCodeInitialized && samplesInitialized && instrumentsInitialized && reaperPackInitialized}
        <div class="alert alert-success">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="font-bold">All components initialized successfully!</h3>
            <div class="text-sm">You're ready to start making music with Renardo. Head to the Code Editor to begin.</div>
          </div>
        </div>
      {/if}
    </div>
  </div>

  <!-- Initialization Components -->
  <div class="collapse collapse-arrow bg-base-200 shadow-md mb-8 {scFilesInitialized && sclangCodeInitialized && samplesInitialized && instrumentsInitialized && reaperPackInitialized ? 'collapse-closed' : 'collapse-open'}">
    <input type="checkbox" />
    <div class="collapse-title text-xl font-medium flex items-center">
      <div class="flex items-center gap-3">
        <div class="{scFilesInitialized && sclangCodeInitialized && samplesInitialized && instrumentsInitialized && reaperPackInitialized ? 'bg-success' : 'bg-base-300'} text-white rounded-full p-1">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.055 2.264-.22 2.944l-.02.089" />
          </svg>
        </div>
        <span>Initialization Components</span>
      </div>
      {#if scFilesInitialized && sclangCodeInitialized && samplesInitialized && instrumentsInitialized && reaperPackInitialized}
        <div class="badge badge-success ml-4">All components initialized</div>
      {:else}
        <div class="badge badge-warning ml-4">Components pending initialization: {5 - [scFilesInitialized, sclangCodeInitialized, samplesInitialized, instrumentsInitialized, reaperPackInitialized].filter(Boolean).length}</div>
      {/if}
    </div>
    <div class="collapse-content">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
        <!-- SuperCollider Classes -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <div class="flex justify-between items-center mb-4">
              <div class="flex items-center gap-3">
                <div class="bg-primary text-primary-content rounded-full w-8 h-8 flex items-center justify-center">1</div>
                <h2 class="card-title title-font">SuperCollider Classes</h2>
              </div>
              {#if scFilesInitialized}
                <div class="badge badge-success gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Initialized
                </div>
              {:else}
                <div class="badge badge-outline gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Pending
                </div>
              {/if}
            </div>

            <p class="text-base-content/70 mb-4">Sets up SuperCollider configuration in your user directory. This is required for sound synthesis.</p>

            <div class="card-actions justify-end">
              <button
                class="btn btn-primary"
                on:click={initSuperColliderClasses}
                disabled={!$appState.connected || scFilesInitialized}
              >
                {#if !scFilesInitialized}
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                  </svg>
                {/if}
                Initialize SuperCollider
              </button>
            </div>
          </div>
        </div>

        <!-- SCLang Code -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <div class="flex justify-between items-center mb-4">
              <div class="flex items-center gap-3">
                <div class="bg-secondary text-secondary-content rounded-full w-8 h-8 flex items-center justify-center">2</div>
                <h2 class="card-title title-font">SCLang Code</h2>
              </div>
              {#if sclangCodeInitialized}
                <div class="badge badge-success gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Downloaded
                </div>
              {:else}
                <div class="badge badge-outline gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Not Installed
                </div>
              {/if}
            </div>

            <p class="text-base-content/70 mb-4">Required SuperCollider language code for special features and advanced functionality.</p>

            <div class="card-actions justify-end">
              {#if !sclangCodeInitialized}
                <button
                  class="btn btn-secondary"
                  on:click={downloadSclangCode}
                  disabled={!$appState.connected || sclangCodeInitialized}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                  </svg>
                  Download SCLang Code
                </button>
              {:else}
                <button class="btn btn-secondary btn-disabled">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Already Installed
                </button>
              {/if}
            </div>
          </div>
        </div>

        <!-- Sample Packs -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <div class="flex justify-between items-center mb-4">
              <div class="flex items-center gap-3">
                <div class="bg-accent text-accent-content rounded-full w-8 h-8 flex items-center justify-center">3</div>
                <h2 class="card-title title-font">Sample Packs</h2>
              </div>
              {#if samplesInitialized}
                <div class="badge badge-success gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Downloaded
                </div>
              {:else}
                <div class="badge badge-outline gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Not Installed
                </div>
              {/if}
            </div>

            <p class="text-base-content/70 mb-4">Sound samples for your compositions including drums, percussion, and various effects.</p>

            <div class="card-actions justify-end">
              {#if !samplesInitialized}
                <button
                  class="btn btn-accent"
                  on:click={goToCollections}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m8.25 3v6.75m0 0l-3-3m3 3l3-3M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
                  </svg>
                  Download Default Samples
                </button>
              {:else}
                <button class="btn btn-accent btn-disabled">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Already Installed
                </button>
              {/if}
            </div>
          </div>
        </div>

        <!-- Instruments & Effects -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <div class="flex justify-between items-center mb-4">
              <div class="flex items-center gap-3">
                <div class="bg-warning text-warning-content rounded-full w-8 h-8 flex items-center justify-center">4</div>
                <h2 class="card-title title-font">Instruments &amp; Effects</h2>
              </div>
              {#if instrumentsInitialized}
                <div class="badge badge-success gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Downloaded
                </div>
              {:else}
                <div class="badge badge-outline gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Not Installed
                </div>
              {/if}
            </div>

            <p class="text-base-content/70 mb-4">Instruments and effects for your compositions, including synths, pads, and audio processors.</p>

            <div class="card-actions justify-end">
              {#if !instrumentsInitialized}
                <button
                  class="btn btn-warning"
                  on:click={goToCollections}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 11-.99-3.467l2.31-.66a2.25 2.25 0 001.632-2.163zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 01-.99-3.467l2.31-.66A2.25 2.25 0 009 15.553z" />
                  </svg>
                  Download Instruments & Effects
                </button>
              {:else}
                <button class="btn btn-warning btn-disabled">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Already Installed
                </button>
              {/if}
            </div>
          </div>
        </div>

        <!-- Reaper Resources Pack -->
        <div class="card bg-base-100 shadow-xl">
          <div class="card-body">
            <div class="flex justify-between items-center mb-4">
              <div class="flex items-center gap-3">
                <div class="bg-error text-error-content rounded-full w-8 h-8 flex items-center justify-center">5</div>
                <h2 class="card-title title-font">Reaper Resources</h2>
              </div>
              {#if reaperPackInitialized}
                <div class="badge badge-success gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Initialized
                </div>
              {:else}
                <div class="badge badge-outline gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Not Installed
                </div>
              {/if}
            </div>

            <p class="text-base-content/70 mb-4">Default Reaper resources including track templates, FX chains, and presets for the Reaper integration.</p>

            <div class="card-actions justify-end">
              {#if !reaperPackInitialized}
                <button
                  class="btn btn-error"
                  on:click={initReaperDefaultPack}
                  disabled={!$appState.connected}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                  </svg>
                  Initialize Reaper Resources
                </button>
              {:else}
                <button class="btn btn-error btn-disabled">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 mr-2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Already Initialized
                </button>
              {/if}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Error messages -->
  {#if $appState.error}
    <div class="alert alert-error mb-8">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>Error: {$appState.error}</span>
    </div>
  {/if}

  <!-- Theme Selector -->
  <ThemeSelector />

  <!-- Explore Further Tutorial Card -->
  <div class="card bg-base-100 shadow-xl mb-8">
    <div class="card-body">
      <h2 class="card-title text-xl title-font">Explore further >></h2>
      <p class="text-base-content/70 mb-4">
        {$appState.welcomeText || 'Create music with the Renardo live coding environment'}
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Live Coding Editor -->
        <div class="card bg-base-200 hover:shadow-md transition-shadow">
          <div class="card-body p-4">
            <div class="flex items-center gap-3 mb-3">
              <div class="bg-success text-success-content rounded-full w-8 h-8 flex items-center justify-center">
                <span class="font-bold">1</span>
              </div>
              <h3 class="text-lg font-medium title-font">Live Coding Editor</h3>
            </div>
            <p class="text-sm mb-4">Create music with the Renardo live coding environment.</p>
            <div class="card-actions justify-end">
              <button class="btn btn-success btn-sm" on:click={() => navigate('editor')}>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.25 9.75L16.5 12l-2.25 2.25m-4.5 0L7.5 12l2.25-2.25M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
                </svg>
                Open Editor
              </button>
            </div>
          </div>
        </div>

        <!-- SuperCollider Backend -->
        <div class="card bg-base-200 hover:shadow-md transition-shadow">
          <div class="card-body p-4">
            <div class="flex items-center gap-3 mb-3">
              <div class="bg-warning text-warning-content rounded-full w-8 h-8 flex items-center justify-center">
                <span class="font-bold">2</span>
              </div>
              <h3 class="text-lg font-medium title-font">Audio Backends</h3>
            </div>
            <p class="text-sm mb-4">Configure and start SuperCollider and REAPER audio backends.</p>
            <div class="card-actions justify-end">
              <button class="btn btn-warning btn-sm" on:click={() => navigate('scbackend')}>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 11-.99-3.467l2.31-.66A2.25 2.25 0 0019.5 12.553v-2.803M9 9l-2.25 6.553M9 9a2.25 2.25 0 00-2.25 2.25v9m0-18c0-.83.67-1.5 1.5-1.5h12c.83 0 1.5.67 1.5 1.5M19.5 21c0 .83-.67 1.5-1.5 1.5h-12c-.83 0-1.5-.67-1.5-1.5" />
                </svg>
                Manage Backend
              </button>
            </div>
          </div>
        </div>

        <!-- Collections -->
        <div class="card bg-base-200 hover:shadow-md transition-shadow">
          <div class="card-body p-4">
            <div class="flex items-center gap-3 mb-3">
              <div class="bg-accent text-accent-content rounded-full w-8 h-8 flex items-center justify-center">
                <span class="font-bold">3</span>
              </div>
              <h3 class="text-lg font-medium title-font">Additional Collections</h3>
            </div>
            <p class="text-sm mb-4">Download additional sample packs and instruments.</p>
            <div class="card-actions justify-end">
              <button class="btn btn-accent btn-sm" on:click={() => navigate('collections')}>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
                </svg>
                Browse Collections
              </button>
            </div>
          </div>
        </div>

        <!-- Configuration -->
        <div class="card bg-base-200 hover:shadow-md transition-shadow">
          <div class="card-body p-4">
            <div class="flex items-center gap-3 mb-3">
              <div class="bg-neutral text-neutral-content rounded-full w-8 h-8 flex items-center justify-center">
                <span class="font-bold">4</span>
              </div>
              <h3 class="text-lg font-medium title-font">Configuration</h3>
            </div>
            <p class="text-sm mb-4">Manage application settings and preferences.</p>
            <div class="card-actions justify-end">
              <button class="btn btn-neutral btn-sm" on:click={() => navigate('config')}>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Settings
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>