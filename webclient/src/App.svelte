<script>
  import { onMount } from 'svelte';
  import { fade, slide } from 'svelte/transition';
  import { appState, initWebSocket, incrementCounter, incrementCounterFallback, sendMessage } from './lib/websocket.js';
  import RenardoInit from './RenardoInit.svelte';
  import CodeEditor from './CodeEditor.svelte';
  import Collections from './Collections.svelte';
  import Configuration from './Configuration.svelte';
  import AudioBackend from './AudioBackend.svelte';
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
  let currentRoute = 'editor'; // Changed default route to 'editor' from 'home'

  // Theme state
  let currentTheme = 'default';
  
  // Zen mode state
  let zenMode = false;

  // Check if WebSockets are supported
  const webSocketSupported = 'WebSocket' in window;

  // Connection state tracking
  let showDisconnectionModal = false;
  let connectionTimer;
  let reconnectAttempts = 0;

  // Monitor connection changes
  $: {
    if ($appState.connected === false && webSocketSupported) {
      // Clear any existing timer
      if (connectionTimer) {
        clearTimeout(connectionTimer);
      }
      
      // Delay showing the disconnection modal to avoid flashing during initial connection
      // or brief network hiccups
      connectionTimer = setTimeout(() => {
        showDisconnectionModal = true;
        reconnectAttempts = 0;
      }, 3000); // Show modal after 3 seconds of being disconnected
      
    } else if ($appState.connected === true) {
      // Clear timer when connection is restored
      if (connectionTimer) {
        clearTimeout(connectionTimer);
        connectionTimer = null;
      }
      
      // Hide modal
      showDisconnectionModal = false;
      reconnectAttempts = 0;
    }
  }
  
  // Track reconnection attempts
  function updateReconnectAttempts() {
    reconnectAttempts++;
  }
  
  // Export the function to be available to the websocket module
  if (typeof window !== 'undefined') {
    window.renardoApp = window.renardoApp || {};
    window.renardoApp.updateReconnectAttempts = updateReconnectAttempts;
  }
  
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
        
        // Changed default route to 'editor' instead of 'home'
        currentRoute = hash || 'editor';
        
        // If empty hash, redirect to editor
        if (!hash) {
          window.location.hash = 'editor';
        }

        // When changing routes, always request the latest status
        if ($appState.connected) {
          sendMessage({ type: 'get_renardo_status' });
        }
      }

      // Initialize route from current hash
      handleHashChange();

      // Listen for hash changes
      window.addEventListener('hashchange', handleHashChange);
      
      // Listen for zen mode changes from CodeEditor
      window.addEventListener('zenModeChange', (event) => {
        zenMode = event.detail.zenMode;
      });

      // Clean up event listeners on component unmount, but keep WebSocket connection
      return () => {
        window.removeEventListener('hashchange', handleHashChange);
        window.removeEventListener('zenModeChange', (event) => {
          zenMode = event.detail.zenMode;
        });
        
        // Clear connection timer if it exists
        if (connectionTimer) {
          clearTimeout(connectionTimer);
          connectionTimer = null;
        }
        
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

<!-- Disconnection Modal -->
{#if showDisconnectionModal && webSocketSupported}
  <div class="modal modal-open" transition:fade={{ duration: 200 }}>
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">Connection Lost</h3>
      <div class="flex flex-col items-center mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-error animate-pulse mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-center mb-2">Connection to the Renardo backend has been lost.</p>
        <p class="text-center text-sm opacity-75 mb-2">Has the Renardo backend application been closed or crashed?</p>
        <div class="badge badge-error gap-2 my-2">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 bg-error"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-error"></span>
          </span>
          Attempting to reconnect automatically... ({reconnectAttempts} attempts)
        </div>
      </div>
      <div class="flex flex-col gap-2">
        <button class="btn btn-primary" onclick="location.reload()">Refresh Page</button>
        <button class="btn btn-outline" onclick="window.close()">Close Tab</button>
      </div>
    </div>
  </div>
{/if}

<div class="drawer">
  <input id="drawer-toggle" type="checkbox" class="drawer-toggle" /> 
  <div class="drawer-content flex flex-col">
    <!-- Navbar -->
    {#if !zenMode || currentRoute !== 'editor'}
      <div class="navbar bg-base-300" transition:slide>
        <div class="navbar-start">
          <label for="drawer-toggle" class="btn btn-square btn-ghost drawer-button lg:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-5 h-5 stroke-current">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          </label>
          <a href="#editor" class="btn btn-ghost text-xl">{zenMode && currentRoute === 'editor' ? 'ฅ^•ﻌ•^ฅ' : 'Renardo ฅ^•ﻌ•^ฅ'}</a>
        </div>
        
        <div class="navbar-center hidden lg:flex">
          <ul class="menu menu-horizontal px-1">
            <li><a href="#editor" class:active={currentRoute === 'editor'}>Code Editor</a></li>
            <li><a href="#init" class:active={currentRoute === 'init'}>Initialize</a></li>
            <li><a href="#scbackend" class:active={currentRoute === 'scbackend'}>Audio Backends</a></li>
            <li><a href="#collections" class:active={currentRoute === 'collections'}>Collections</a></li>
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
    {/if}

    <!-- Main content -->
    <div class="min-h-screen bg-base-100">
      {#if currentRoute === 'editor'}
        <CodeEditor />
      {:else if currentRoute === 'init'}
        <!-- Component-specific content -->
        <RenardoInit />
      {:else if currentRoute === 'collections'}
        <Collections />
      {:else if currentRoute === 'config'}
        <Configuration />
      {:else if currentRoute === 'scbackend'}
        <AudioBackend />
      {/if}
    </div>
  </div>
  
  <!-- Mobile drawer sidebar -->
  <div class="drawer-side z-50">
    <label for="drawer-toggle" aria-label="close sidebar" class="drawer-overlay"></label>
    <ul class="menu p-4 w-64 min-h-full bg-base-200 text-base-content">
      <li class="menu-title">Renardo ฅ^•ﻌ•^ฅ</li>
      <li><a href="#editor" class:active={currentRoute === 'editor'}>Code Editor</a></li>
      <li><a href="#init" class:active={currentRoute === 'init'}>Initialize</a></li>
      <li><a href="#scbackend" class:active={currentRoute === 'scbackend'}>Audio Backends</a></li>
      <li><a href="#collections" class:active={currentRoute === 'collections'}>Collections</a></li>
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