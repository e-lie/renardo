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

  // Navigate to collections
  function goToCollections() {
    window.location.hash = '#collections';
  }
</script>

<div class="container mx-auto px-4 py-8 max-w-4xl">
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
            <div class="stat-value text-primary">{[scFilesInitialized, sclangCodeInitialized, samplesInitialized, instrumentsInitialized].filter(Boolean).length}/4</div>
            <div class="stat-desc">Components initialized and ready to use</div>
          </div>
        </div>
      </div>

      <!-- Success message when all components are initialized -->
      {#if scFilesInitialized && sclangCodeInitialized && samplesInitialized && instrumentsInitialized}
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

  <!-- Error messages -->
  {#if $appState.error}
    <div class="alert alert-error mb-8">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>Error: {$appState.error}</span>
    </div>
  {/if}

  <!-- Initialization Components -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
  </div>
</div>