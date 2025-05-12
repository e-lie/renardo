<script>
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { appState, initWebSocket, incrementCounter, incrementCounterFallback, sendMessage } from './lib/websocket.js';
  import RenardoInit from './RenardoInit.svelte';
  import CodeEditor from './CodeEditor.svelte';
  import Collections from './Collections.svelte';
  import Configuration from './Configuration.svelte';
  import SuperColliderBackend from './SuperColliderBackend.svelte';

  // Add CodeMirror CSS links to the document head
  if (typeof document !== 'undefined') {
    // Add CodeMirror CSS
    const cmCss = document.createElement('link');
    cmCss.rel = 'stylesheet';
    cmCss.href = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css';
    document.head.appendChild(cmCss);

    // Add CodeMirror theme (you can change the theme as needed)
    const cmThemeCss = document.createElement('link');
    cmThemeCss.rel = 'stylesheet';
    cmThemeCss.href = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/monokai.min.css';
    document.head.appendChild(cmThemeCss);

    // Add CodeMirror script (if it's not already imported)
    if (typeof window.CodeMirror === 'undefined') {
      const cmJs = document.createElement('script');
      cmJs.src = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js';

      // Wait for main script to load before loading mode
      cmJs.onload = function() {
        // Add Python mode for CodeMirror
        const cmPythonJs = document.createElement('script');
        cmPythonJs.src = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/python/python.min.js';
        document.head.appendChild(cmPythonJs);
      };

      document.head.appendChild(cmJs);
    }
  }

  // Router state
  let currentRoute = 'home';

  // Check if WebSockets are supported
  const webSocketSupported = 'WebSocket' in window;

  // Initialize WebSocket connection on mount
  onMount(() => {
    if (webSocketSupported) {
      // Initialize WebSocket connection once for the entire application
      initWebSocket();

      // Request status after a short delay
      setTimeout(() => {
        if ($appState.connected) {
          // Get initial state and status
          sendMessage({ type: 'get_state' });
          sendMessage({ type: 'get_renardo_status' });
        }
      }, 500);

      // Simple router based on URL hash
      function handleHashChange() {
        const hash = window.location.hash.replace('#', '');
        currentRoute = hash || 'home';

        // When changing routes, always request the latest status
        if ($appState.connected) {
          sendMessage({ type: 'get_renardo_status' });
        }
      }

      // Initialize route from current hash
      handleHashChange();

      // Listen for hash changes
      window.addEventListener('hashchange', handleHashChange);

      // Clean up event listeners on component unmount, but keep WebSocket connection
      return () => {
        window.removeEventListener('hashchange', handleHashChange);
        // Do NOT close the WebSocket here - it should stay open for the app's lifetime
      };
    } else {
      // Fallback for browsers without WebSocket support
      fetchStateFromAPI();
    }
  });

  // Fallback function to fetch state from REST API
  async function fetchStateFromAPI() {
    try {
      const response = await fetch('/api/state');
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      const data = await response.json();

      $appState = {
        ...$appState,
        counter: data.counter,
        welcomeText: data.welcome_text,
        error: null
      };
    } catch (error) {
      console.error('Error fetching state:', error);
      $appState.error = 'Failed to fetch state from server';
    }
  }

  // Handle counter increment
  function handleIncrement() {
    if (webSocketSupported) {
      incrementCounter();
    } else {
      incrementCounterFallback();
    }
  }

  // Navigation
  function navigate(route) {
    window.location.hash = `#${route}`;
    currentRoute = route;
  }
</script>

<div class="drawer">
  <input id="drawer-toggle" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content flex flex-col">
    <!-- Navbar -->
    <div class="navbar bg-base-300">
      <div class="navbar-start">
        <label for="drawer-toggle" class="btn btn-square btn-ghost drawer-button lg:hidden">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </label>
        <a href="#home" class="btn btn-ghost text-xl">Renardo Web</a>
      </div>

      <div class="navbar-center hidden lg:flex">
        <ul class="menu menu-horizontal px-1">
          <li><a href="#home" class:active={currentRoute === 'home'}>Home</a></li>
          <li><a href="#init" class:active={currentRoute === 'init'}>Initialize</a></li>
          <li><a href="#editor" class:active={currentRoute === 'editor'}>Code Editor</a></li>
          <li><a href="#collections" class:active={currentRoute === 'collections'}>Collections</a></li>
          <li><a href="#scbackend" class:active={currentRoute === 'scbackend'}>SuperCollider</a></li>
          <li><a href="#config" class:active={currentRoute === 'config'}>Settings</a></li>
        </ul>
      </div>

      <div class="navbar-end">
        {#if webSocketSupported}
          <div class="badge {$appState.connected ? 'badge-success' : 'badge-error'} gap-2">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 {$appState.connected ? 'bg-success' : 'bg-error'}"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 {$appState.connected ? 'bg-success' : 'bg-error'}"></span>
            </span>
            {$appState.connected ? 'Connected' : 'Disconnected'}
          </div>
        {:else}
          <div class="badge badge-warning gap-2">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 bg-warning"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-warning"></span>
            </span>
            HTTP Fallback
          </div>
        {/if}
      </div>
    </div>

    <!-- Main content -->
    <div class="min-h-screen bg-base-100">
      {#if currentRoute === 'home'}
        <div class="hero min-h-[30vh] bg-base-200">
          <div class="hero-content text-center">
            <div class="max-w-md">
              <h1 class="text-5xl font-bold">Renardo Web</h1>
              <p class="py-6">{$appState.welcomeText || 'Create music with the Renardo live coding environment'}</p>
            </div>
          </div>
        </div>

        <div class="container mx-auto px-4 py-8">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- Initialize Card -->
            <div class="card bg-base-100 shadow-xl">
              <figure class="px-10 pt-10">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 text-primary">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                </svg>
              </figure>
              <div class="card-body items-center text-center">
                <h2 class="card-title">Initialize Renardo</h2>
                <p>Set up SuperCollider, download samples, and install instruments.</p>
                <div class="card-actions">
                  <button class="btn btn-primary" on:click={() => navigate('init')}>Get Started</button>
                </div>
              </div>
            </div>

            <!-- Editor Card -->
            <div class="card bg-base-100 shadow-xl">
              <figure class="px-10 pt-10">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 text-success">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.25 9.75L16.5 12l-2.25 2.25m-4.5 0L7.5 12l2.25-2.25M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
                </svg>
              </figure>
              <div class="card-body items-center text-center">
                <h2 class="card-title">Live Coding Editor</h2>
                <p>Create music with the Renardo live coding environment.</p>
                <div class="card-actions">
                  <button class="btn btn-success" on:click={() => navigate('editor')}>Open Editor</button>
                </div>
              </div>
            </div>

            <!-- SuperCollider Card -->
            <div class="card bg-base-100 shadow-xl">
              <figure class="px-10 pt-10">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 text-warning">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 11-.99-3.467l2.31-.66A2.25 2.25 0 0019.5 12.553v-2.803M9 9l-2.25 6.553M9 9a2.25 2.25 0 00-2.25 2.25v9m0-18c0-.83.67-1.5 1.5-1.5h12c.83 0 1.5.67 1.5 1.5M19.5 21c0 .83-.67 1.5-1.5 1.5h-12c-.83 0-1.5-.67-1.5-1.5" />
                </svg>
              </figure>
              <div class="card-body items-center text-center">
                <h2 class="card-title">SuperCollider Backend</h2>
                <p>Configure and start the SuperCollider sound synthesis engine.</p>
                <div class="card-actions">
                  <button class="btn btn-warning" on:click={() => navigate('scbackend')}>Manage Backend</button>
                </div>
              </div>
            </div>

            <!-- Collections Card -->
            <div class="card bg-base-100 shadow-xl">
              <figure class="px-10 pt-10">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 text-accent">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
                </svg>
              </figure>
              <div class="card-body items-center text-center">
                <h2 class="card-title">Additional Collections</h2>
                <p>Download additional sample packs and instruments.</p>
                <div class="card-actions">
                  <button class="btn btn-accent" on:click={() => navigate('collections')}>Browse Collections</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Error messages -->
          {#if $appState.error}
            <div class="alert alert-error mt-8">
              <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <span>Error: {$appState.error}</span>
            </div>
          {/if}
        </div>
      {:else if currentRoute === 'init'}
        <RenardoInit />
      {:else if currentRoute === 'editor'}
        <CodeEditor />
      {:else if currentRoute === 'collections'}
        <Collections />
      {:else if currentRoute === 'config'}
        <Configuration />
      {:else if currentRoute === 'scbackend'}
        <SuperColliderBackend />
      {/if}
    </div>
  </div>

  <!-- Mobile drawer sidebar -->
  <div class="drawer-side z-50">
    <label for="drawer-toggle" aria-label="close sidebar" class="drawer-overlay"></label>
    <ul class="menu p-4 w-64 min-h-full bg-base-200 text-base-content">
      <li class="menu-title">Renardo Web</li>
      <li><a href="#home" class:active={currentRoute === 'home'}>Home</a></li>
      <li><a href="#init" class:active={currentRoute === 'init'}>Initialize</a></li>
      <li><a href="#editor" class:active={currentRoute === 'editor'}>Code Editor</a></li>
      <li><a href="#collections" class:active={currentRoute === 'collections'}>Collections</a></li>
      <li><a href="#scbackend" class:active={currentRoute === 'scbackend'}>SuperCollider</a></li>
      <li><a href="#config" class:active={currentRoute === 'config'}>Settings</a></li>
    </ul>
  </div>
</div>