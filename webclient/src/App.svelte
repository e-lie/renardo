<script>
  import { onMount } from 'svelte';
  import { appState, initWebSocket, incrementCounter, incrementCounterFallback } from './lib/websocket.js';
  import RenardoInit from './RenardoInit.svelte';
  import CodeEditor from './CodeEditor.svelte';
  
  // Router state
  let currentRoute = 'home';
  
  // Check if WebSockets are supported
  const webSocketSupported = 'WebSocket' in window;
  
  // Initialize WebSocket connection on mount
  onMount(() => {
    if (webSocketSupported) {
      initWebSocket();
      
      // Simple router based on URL hash
      function handleHashChange() {
        const hash = window.location.hash.replace('#', '');
        currentRoute = hash || 'home';
      }
      
      // Initialize route from current hash
      handleHashChange();
      
      // Listen for hash changes
      window.addEventListener('hashchange', handleHashChange);
      
      // Clean up WebSocket and event listeners on component unmount
      return () => {
        window.removeEventListener('hashchange', handleHashChange);
        // WebSocket cleanup handled in websocket.js
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

<header>
  <nav>
    <div class="nav-logo">Renardo Web</div>
    <div class="nav-links">
      <a href="#home" class:active={currentRoute === 'home'}>Home</a>
      <a href="#init" class:active={currentRoute === 'init'}>Initialize</a>
      <a href="#editor" class:active={currentRoute === 'editor'}>Code Editor</a>
    </div>
  </nav>
</header>

<main>
  {#if currentRoute === 'home'}
    <div class="container">
      <h1>Welcome to Renardo Web</h1>
      
      <!-- Connection status -->
      <div class="status-bar">
        {#if webSocketSupported}
          <div class="status-indicator" class:connected={$appState.connected}>
            {$appState.connected ? 'Connected' : 'Disconnected'}
          </div>
        {:else}
          <div class="status-indicator fallback">
            Using HTTP Fallback (WebSockets not supported)
          </div>
        {/if}
      </div>
      
      <!-- Welcome text from server -->
      <div class="welcome-message">
        <h2>{$appState.welcomeText}</h2>
      </div>
      
      <!-- Main content -->
      <div class="main-content">
        <div class="feature-card">
          <h3>Initialize Renardo</h3>
          <p>Set up SuperCollider, download samples, and install instruments.</p>
          <button on:click={() => navigate('init')}>Get Started</button>
        </div>
        
        <div class="feature-card">
          <h3>Live Coding Editor</h3>
          <p>Create music with the Renardo live coding environment.</p>
          <button on:click={() => navigate('editor')} class="editor-button">
            Open Editor
          </button>
        </div>
      </div>
      
      <!-- Error messages -->
      {#if $appState.error}
        <div class="error-message">
          Error: {$appState.error}
        </div>
      {/if}
    </div>
  {:else if currentRoute === 'init'}
    <RenardoInit />
  {:else if currentRoute === 'editor'}
    <CodeEditor />
  {/if}
</main>
  
  <style>
    :global(body) {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
        Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      background-color: #f5f5f5;
      color: #333;
    }
    
    header {
      background-color: #2c3e50;
      padding: 1rem 2rem;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      position: sticky;
      top: 0;
      z-index: 100;
    }
    
    nav {
      display: flex;
      justify-content: space-between;
      align-items: center;
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .nav-logo {
      color: white;
      font-size: 1.5rem;
      font-weight: bold;
    }
    
    .nav-links {
      display: flex;
      gap: 1.5rem;
    }
    
    .nav-links a {
      color: #ecf0f1;
      text-decoration: none;
      font-size: 1rem;
      padding: 0.5rem 0;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;
    }
    
    .nav-links a:hover {
      color: white;
      border-bottom-color: #3498db;
    }
    
    .nav-links a.active {
      color: white;
      border-bottom-color: #3498db;
    }
    
    main {
      width: 100%;
      min-height: calc(100vh - 4rem);
      display: flex;
      justify-content: center;
      align-items: flex-start;
      padding: 0;
    }
    
    .container {
      max-width: 800px;
      width: 100%;
      padding: 2rem;
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      margin-top: 2rem;
    }
    
    h1 {
      text-align: center;
      margin-top: 0;
      color: #2c3e50;
    }
    
    .status-bar {
      display: flex;
      justify-content: center;
      margin-bottom: 1.5rem;
    }
    
    .status-indicator {
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.875rem;
      font-weight: 500;
      background-color: #f44336;
      color: white;
    }
    
    .status-indicator.connected {
      background-color: #4caf50;
    }
    
    .status-indicator.fallback {
      background-color: #ff9800;
    }
    
    .welcome-message {
      text-align: center;
      margin-bottom: 2rem;
    }
    
    .welcome-message h2 {
      margin: 0;
      color: #3498db;
    }
    
    .main-content {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      margin-bottom: 2rem;
    }
    
    @media (max-width: 768px) {
      .main-content {
        grid-template-columns: 1fr;
      }
    }
    
    .feature-card {
      border: 1px solid #e0e0e0;
      border-radius: 6px;
      padding: 1.5rem;
      background-color: #fafafa;
    }
    
    .feature-card h3 {
      margin-top: 0;
      color: #2c3e50;
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
    }
    
    button:hover {
      background-color: #2980b9;
    }
    
    button:active {
      transform: translateY(1px);
    }
    
    .editor-button {
      background-color: #2ecc71;
    }
    
    .editor-button:hover {
      background-color: #27ae60;
    }
    
    .error-message {
      background-color: #ffebee;
      color: #c62828;
      padding: 1rem;
      border-radius: 4px;
      margin-top: 1.5rem;
    }
  </style>