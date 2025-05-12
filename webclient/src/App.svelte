<script>
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { appState, initWebSocket, incrementCounter, incrementCounterFallback, sendMessage } from './lib/websocket.js';
  import RenardoInit from './RenardoInit.svelte';
  import CodeEditor from './CodeEditor.svelte';
  import Collections from './Collections.svelte';
  import Configuration from './Configuration.svelte';
  import SuperColliderBackend from './SuperColliderBackend.svelte';
  import ThemeSelector from './lib/ThemeSelector.svelte';
  import ThemeButton from './lib/ThemeButton.svelte';
  
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

  // Theme state
  let currentTheme = 'default';

  // Check if WebSockets are supported
  const webSocketSupported = 'WebSocket' in window;
  
  // Initialize WebSocket connection on mount
  onMount(() => {
    // Initialize theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      currentTheme = savedTheme;
      document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
      document.documentElement.setAttribute('data-theme', currentTheme);
      localStorage.setItem('theme', currentTheme);
    }

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

  // Set theme
  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    currentTheme = theme;
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
        <a href="#home" class="btn btn-ghost text-xl">Renardo ฅ^•ﻌ•^ฅ</a>
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
        <!-- Theme Button -->
        <!-- <ThemeButton /> To fix ! -->

        {#if webSocketSupported}
          <div class="badge {$appState.connected ? 'badge-success' : 'badge-error'} gap-2 ml-2">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 {$appState.connected ? 'bg-success' : 'bg-error'}"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 {$appState.connected ? 'bg-success' : 'bg-error'}"></span>
            </span>
            {$appState.connected ? 'Connected' : 'Disconnected'}
          </div>
        {:else}
          <div class="badge badge-warning gap-2 ml-2">
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
        <div class="container mx-auto px-4 py-8 max-w-4xl">
          <div class="text-center mb-8">
            <h1 class="text-3xl font-bold mb-2 title-font">Renardo (Web)</h1>
            <p class="text-base-content/70">
              {$appState.welcomeText || 'Create music with the Renardo live coding environment'}
            </p>
          </div>

          <!-- Getting Started Tutorial Card -->
          <div class="card bg-base-100 shadow-xl mb-8">
            <div class="card-body">
              <h2 class="card-title text-xl title-font">Getting Started >></h2>
              <p class="text-base-content/70 mb-4">
                Follow these steps to setup and use Renardo for live music coding.
              </p>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Initialize -->
                <div class="card bg-base-200 hover:shadow-md transition-shadow">
                  <div class="card-body p-4">
                    <div class="flex items-center gap-3 mb-3">
                      <div class="bg-primary text-primary-content rounded-full w-8 h-8 flex items-center justify-center">
                        <span class="font-bold">1</span>
                      </div>
                      <h3 class="text-lg font-medium title-font">Initialize Renardo</h3>
                    </div>
                    <p class="text-sm mb-4">Set up SuperCollider, download samples, and install instruments.</p>
                    <div class="card-actions justify-end">
                      <button class="btn btn-primary btn-sm" on:click={() => navigate('init')}>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                        </svg>
                        Get Started
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Live Coding Editor -->
                <div class="card bg-base-200 hover:shadow-md transition-shadow">
                  <div class="card-body p-4">
                    <div class="flex items-center gap-3 mb-3">
                      <div class="bg-success text-success-content rounded-full w-8 h-8 flex items-center justify-center">
                        <span class="font-bold">2</span>
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
                        <span class="font-bold">3</span>
                      </div>
                      <h3 class="text-lg font-medium title-font">SuperCollider Backend</h3>
                    </div>
                    <p class="text-sm mb-4">Configure and start the SuperCollider sound synthesis engine.</p>
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
                        <span class="font-bold">4</span>
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
                <div class="card bg-base-200 hover:shadow-md transition-shadow md:col-span-2">
                  <div class="card-body p-4">
                    <div class="flex items-center gap-3 mb-3">
                      <div class="bg-neutral text-neutral-content rounded-full w-8 h-8 flex items-center justify-center">
                        <span class="font-bold">5</span>
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

          <!-- Theme Selector -->
          <ThemeSelector />

          <!-- Status Card -->
          {#if webSocketSupported}
            <div class="card bg-base-100 shadow-xl mb-8">
              <div class="card-body">
                <h2 class="card-title title-font">System Status >></h2>
                <div class="overflow-x-auto">
                  <table class="table table-zebra">
                    <tbody>
                      <tr>
                        <td class="font-medium">WebSocket Connection</td>
                        <td>
                          {#if $appState.connected}
                            <div class="badge badge-success gap-2">
                              <span class="relative flex h-2 w-2">
                                <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 bg-success"></span>
                                <span class="relative inline-flex rounded-full h-2 w-2 bg-success"></span>
                              </span>
                              Connected
                            </div>
                          {:else}
                            <div class="badge badge-error gap-2">
                              <span class="relative flex h-2 w-2">
                                <span class="relative inline-flex rounded-full h-2 w-2 bg-error"></span>
                              </span>
                              Disconnected
                            </div>
                          {/if}
                        </td>
                      </tr>
                      {#if $appState.runtimeStatus}
                        <tr>
                          <td class="font-medium">SuperCollider Backend</td>
                          <td>
                            {#if $appState.runtimeStatus.scBackendRunning}
                              <div class="badge badge-success gap-2">Running</div>
                            {:else}
                              <div class="badge badge-error gap-2">Stopped</div>
                            {/if}
                          </td>
                        </tr>
                        <tr>
                          <td class="font-medium">Renardo Runtime</td>
                          <td>
                            {#if $appState.runtimeStatus.renardoRuntimeRunning}
                              <div class="badge badge-success gap-2">Running</div>
                            {:else}
                              <div class="badge badge-error gap-2">Stopped</div>
                            {/if}
                          </td>
                        </tr>
                      {/if}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          {/if}

          <!-- Error messages -->
          {#if $appState.error}
            <div class="alert alert-error mb-8">
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
      <li class="menu-title">Renardo ฅ^•ﻌ•^ฅ</li>
      <li><a href="#home" class:active={currentRoute === 'home'}>Home</a></li>
      <li><a href="#init" class:active={currentRoute === 'init'}>Initialize</a></li>
      <li><a href="#editor" class:active={currentRoute === 'editor'}>Code Editor</a></li>
      <li><a href="#collections" class:active={currentRoute === 'collections'}>Collections</a></li>
      <li><a href="#scbackend" class:active={currentRoute === 'scbackend'}>SuperCollider</a></li>
      <li><a href="#config" class:active={currentRoute === 'config'}>Settings</a></li>

      <!-- Divider -->
      <div class="divider my-2"></div>

      <!-- Mobile Theme Options -->
      <li class="menu-title title-font">Choose Theme</li>
      <div class="grid grid-cols-2 gap-2 p-2">
        <button class="btn btn-sm {currentTheme === 'default' ? 'btn-primary' : 'btn-outline'}" on:click={() => setTheme('default')}>
          🦄 Default
        </button>
        <button class="btn btn-sm {currentTheme === 'synthwave' ? 'btn-primary' : 'btn-outline'}" on:click={() => setTheme('synthwave')}>
          🎸 Synthwave
        </button>
        <button class="btn btn-sm {currentTheme === 'coffee' ? 'btn-primary' : 'btn-outline'}" on:click={() => setTheme('coffee')}>
          ☕ Coffee
        </button>
        <button class="btn btn-sm {currentTheme === 'pastel' ? 'btn-primary' : 'btn-outline'}" on:click={() => setTheme('pastel')}>
          🎨 Pastel
        </button>
        <button class="btn btn-sm {currentTheme === 'cyberpunk' ? 'btn-primary' : 'btn-outline'}" on:click={() => setTheme('cyberpunk')}>
          🤖 Cyberpunk
        </button>
      </div>
    </ul>
  </div>
</div>