<script>
    import { onMount } from 'svelte';
    import { appState, initWebSocket, incrementCounter, incrementCounterFallback } from './lib/websocket.js';
    
    // Check if WebSockets are supported
    const webSocketSupported = 'WebSocket' in window;
    
    // Initialize WebSocket connection on mount
    onMount(() => {
      if (webSocketSupported) {
        initWebSocket();
        
        // Clean up WebSocket on component unmount
        return () => {
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
  </script>
  
  <main>
    <div class="container">
      <h1>Flask + Svelte + WebSocket</h1>
      
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
      
      <!-- Counter section -->
      <div class="counter-section">
        <h3>Counter: <span class="counter-value">{$appState.counter}</span></h3>
        <button on:click={handleIncrement}>
          Increment Counter
        </button>
        <p class="counter-description">
          Click the button to increase the counter on the server.
          All connected clients will see the updated value in real-time.
        </p>
      </div>
      
      <!-- Error messages -->
      {#if $appState.error}
        <div class="error-message">
          Error: {$appState.error}
        </div>
      {/if}
    </div>
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
    
    main {
      width: 100%;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    
    .container {
      max-width: 600px;
      width: 100%;
      padding: 2rem;
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
    
    .counter-section {
      text-align: center;
      margin-bottom: 2rem;
    }
    
    .counter-value {
      font-size: 1.25em;
      color: #e74c3c;
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
    
    .counter-description {
      margin-top: 1rem;
      font-size: 0.9rem;
      color: #7f8c8d;
    }
    
    .error-message {
      background-color: #ffebee;
      color: #c62828;
      padding: 1rem;
      border-radius: 4px;
      margin-top: 1.5rem;
    }
  </style>