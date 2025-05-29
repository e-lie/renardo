import { writable } from 'svelte/store';

// Create stores for application state
export const appState = writable({
  counter: 0,
  welcomeText: 'Loading...',
  connected: false,
  error: null,
  // Add Renardo initialization state
  renardoInit: {
    superColliderClasses: false,
    sclangCode: false,
    samples: false,
    instruments: false,
    reaperPack: false,
    startupFiles: false
  },
  // Add runtime status
  runtimeStatus: {
    scBackendRunning: false,
    scBackendStartupCode: 'Renardo.start; Renardo.midi;',
    renardoRuntimeRunning: false
  },
  // Add log messages array
  logMessages: [],
  // Add console output array
  consoleOutput: [],
  // Last received message for event detection
  _lastMessage: null
});

// WebSocket connection
let socket;
let reconnectTimer;
let pingTimer;
const MAX_RECONNECT_DELAY = 2000; // Reduced from 5000ms to 2000ms for faster reconnection
const BASE_RECONNECT_DELAY = 300; // Base delay of 300ms instead of 1000ms
const RECONNECT_FACTOR = 1.2; // Reduced exponential factor from 1.5 to 1.2
const MAX_RECONNECT_ATTEMPTS = 10; // Reset backoff after this many attempts
let reconnectAttempts = 0;
const PING_INTERVAL = 30000; // 30 seconds

/**
 * Initialize WebSocket connection
 */
export function initWebSocket() {
  // Close any existing connection
  if (socket) {
    socket.close();
  }

  // Clear any existing timers
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
  
  if (pingTimer) {
    clearInterval(pingTimer);
    pingTimer = null;
  }
  
  // Determine WebSocket URL based on current location
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = import.meta.env.DEV 
    ? 'ws://localhost:12345/ws'  // Development
    : `${protocol}//${window.location.host}/ws`;  // Production

  // Create WebSocket connection
  socket = new WebSocket(wsUrl);
  
  // Connection opened
  socket.addEventListener('open', () => {
    console.log('WebSocket connection established');
    reconnectAttempts = 0;
    
    // Update store to indicate connected status
    appState.update(state => ({
      ...state,
      connected: true,
      error: null
    }));
    
    // Request initial state
    sendMessage({
      type: 'get_state'
    });
    
    // Request Renardo initialization status
    sendMessage({
      type: 'get_renardo_status'
    });
    
    // Set up a ping interval to keep the connection alive
    pingTimer = setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        // Send a ping message to prevent the connection from closing
        sendMessage({
          type: 'ping',
          timestamp: Date.now()
        });
      }
    }, PING_INTERVAL);
  });
  
  // Connection closed
  socket.addEventListener('close', (event) => {
    console.log('WebSocket connection closed', event);
    
    // Clear ping timer if it exists
    if (pingTimer) {
      clearInterval(pingTimer);
      pingTimer = null;
    }
    
    // Update store to indicate disconnected status with reconnection information
    appState.update(state => ({
      ...state,
      connected: false,
      error: 'Connection lost. Reconnecting automatically...'
    }));
    
    // Don't reconnect for clean closes with certain codes
    if (event.wasClean && (event.code === 1000 || event.code === 1001)) {
      console.log('Clean close, not reconnecting automatically');
      return;
    }
    
    // Attempt to reconnect with faster exponential backoff
    const delay = Math.min(BASE_RECONNECT_DELAY * Math.pow(RECONNECT_FACTOR, reconnectAttempts), MAX_RECONNECT_DELAY);
    reconnectAttempts++;
    
    // Reset reconnect attempts counter after MAX_RECONNECT_ATTEMPTS to prevent prolonged backoffs
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.log(`Reached maximum reconnect attempts (${MAX_RECONNECT_ATTEMPTS}), resetting backoff timer`);
      reconnectAttempts = 0;
    }
    
    console.log(`Attempting to reconnect (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}) in ${delay}ms...`);
    
    // Notify the app about reconnection attempt if the function is available
    if (window.renardoApp && typeof window.renardoApp.updateReconnectAttempts === 'function') {
      window.renardoApp.updateReconnectAttempts();
    }
    reconnectTimer = setTimeout(initWebSocket, delay);
  });
  
  // Connection error
  socket.addEventListener('error', (error) => {
    console.error('WebSocket error:', error);
    
    // Update store with error
    appState.update(state => ({
      ...state,
      error: 'Connection error. Attempting to reconnect...'
    }));
  });
  
  // Message received
  socket.addEventListener('message', (event) => {
    try {
      const message = JSON.parse(event.data);
      handleMessage(message);
    } catch (error) {
      console.error('Error parsing message:', error);
    }
  });
}

/**
 * Handle incoming WebSocket messages
 */
function handleMessage(message) {
  const { type, data, error, message: errorMessage } = message;
  
  // Always store the last message in the state for components to detect specific events
  appState.update(state => ({
    ...state,
    _lastMessage: message
  }));
  
  switch (type) {
    case 'initial_state':
    case 'state_updated':
      // Update application state
      appState.update(state => ({
        ...state,
        counter: data.counter,
        welcomeText: data.welcome_text,
        error: null,
        // Update Renardo initialization status if available
        renardoInit: data.renardo_init || state.renardoInit,
        // Update runtime status if available
        runtimeStatus: data.runtime_status || state.runtimeStatus,
      }));
      break;
      
    case 'renardo_status':
      // Update Renardo initialization status
      appState.update(state => ({
        ...state,
        renardoInit: data.initStatus || data.data?.initStatus || state.renardoInit,
        error: null
      }));
      break;
      
    case 'sc_backend_status':
      // Update SC backend runtime status
      appState.update(state => ({
        ...state,
        runtimeStatus: {
          ...state.runtimeStatus,
          scBackendRunning: data.running || false
        },
        error: null
      }));
      break;
      
    case 'setting_updated':
      // Update application state with the new setting value
      console.log('Setting updated via websocket:', data.key, data.value);
      // We'll let the Configuration component handle this via the _lastMessage property
      break;
      
    case 'settings_reset':
      // Update application state with all reset settings
      console.log('Settings reset via websocket');
      // We'll let the Configuration component handle this via the _lastMessage property
      break;
      
    case 'log_message':
      // Add new log message to the array
      appState.update(state => {
        // Create a new log messages array with the new message added
        const updatedLogMessages = [...state.logMessages, {
          timestamp: data.timestamp || new Date().toLocaleTimeString(),
          level: data.level || 'INFO',
          message: data.message
        }];
        
        // Limit log messages to the most recent 500 (prevent too much memory usage)
        const trimmedLogMessages = updatedLogMessages.slice(-500);
        
        return {
          ...state,
          logMessages: trimmedLogMessages
        };
      });
      break;
      
    case 'console_output':
      // Add new console output to the array
      appState.update(state => {
        // Check if this is a duplicate message
        const lastMessage = state.consoleOutput.length > 0
          ? state.consoleOutput[state.consoleOutput.length - 1]
          : null;

        // Skip if this is a duplicate of the last message
        if (lastMessage &&
            lastMessage.level === (data.level || 'info') &&
            lastMessage.message === data.message) {
          // It's a duplicate, don't add it
          return state;
        }

        // Create a new console output array with the new output added
        const updatedConsoleOutput = [...state.consoleOutput, {
          // No timestamp needed
          level: data.level || 'info',
          message: data.message
        }];

        // Limit console output to the most recent 1000 entries
        const trimmedConsoleOutput = updatedConsoleOutput.slice(-1000);

        return {
          ...state,
          consoleOutput: trimmedConsoleOutput
        };
      });
      break;
      
    case 'code_execution_result':
      // Dispatch custom event for code execution completion (for highlighting removal)
      if (typeof window !== 'undefined' && data.requestId) {
        const event = new CustomEvent('codeExecutionComplete', { 
          detail: { 
            requestId: data.requestId, 
            success: data.success 
          } 
        });
        window.dispatchEvent(event);
      }
      
      // Handle code execution result
      if (data.success) {
        // Only add the message if there's actual content to show
        if (data.message && data.message.trim()) {
          // Add success message to console output
          // Check if this is a duplicate message
          appState.update(state => {
            // Check if the last message is identical to avoid duplicates
            const lastMessage = state.consoleOutput.length > 0
              ? state.consoleOutput[state.consoleOutput.length - 1]
              : null;

            // Skip if this is a duplicate of the last message
            if (lastMessage &&
                lastMessage.level === 'success' &&
                lastMessage.message === data.message) {
              // It's a duplicate, don't add it
              return state;
            }

            // It's not a duplicate, so add it
            const updatedConsoleOutput = [...state.consoleOutput, {
              // No timestamp needed
              level: 'success',
              message: data.message
            }];

            const trimmedConsoleOutput = updatedConsoleOutput.slice(-1000);

            return {
              ...state,
              consoleOutput: trimmedConsoleOutput,
              error: null
            };
          });
        }
      } else {
        // Add error message to console output (errors always show)
        appState.update(state => {
          // Check if this is a duplicate message
          const lastMessage = state.consoleOutput.length > 0
            ? state.consoleOutput[state.consoleOutput.length - 1]
            : null;

          // Skip if this is a duplicate of the last message
          if (lastMessage &&
              lastMessage.level === 'error' &&
              lastMessage.message === (data.message || 'Code execution failed')) {
            // It's a duplicate, don't add it
            return state;
          }

          const updatedConsoleOutput = [...state.consoleOutput, {
            // No timestamp needed
            level: 'error',
            message: data.message || 'Code execution failed'
          }];

          const trimmedConsoleOutput = updatedConsoleOutput.slice(-1000);

          return {
            ...state,
            consoleOutput: trimmedConsoleOutput,
            error: null
          };
        });
      }
      break;
      
    case 'init_complete':
      // Update specific init status flag
      appState.update(state => {
        const updatedRenardoInit = {
          ...state.renardoInit,
          [data.component]: data.success
        };
        
        return {
          ...state,
          renardoInit: updatedRenardoInit
        };
      });
      break;
      
    case 'error':
      // Handle error message
      console.error('Server error:', errorMessage || error);
      appState.update(state => ({
        ...state,
        error: errorMessage || error || 'Unknown server error'
      }));
      break;
      
    case 'collection_downloaded':
      // Handle collection download notification
      console.log(`Collection downloaded: ${data.type}/${data.name}`);
      // If the collections page is open, it will automatically refresh
      // when the user navigates to it next time
      break;
      
    case 'pong':
      // Received pong response from server - connection is healthy
      // We can optionally measure round-trip time for diagnostics
      const roundTripTime = Date.now() - (message.timestamp || Date.now());
      console.debug(`Received pong, RTT: ${roundTripTime}ms`);
      break;
      
    case 'reaper_reinit_result':
      console.log('RECEIVED REAPER RESET RESULT:', message);
      // This will be handled by the AudioBackend component via _lastMessage
      break;
      
    case 'reaper_launch_result':
      console.log('RECEIVED REAPER LAUNCH RESULT:', message);
      // This will be handled by the AudioBackend component via _lastMessage
      break;
      
    case 'reaper_test_result':
      console.log('RECEIVED REAPER TEST RESULT:', message);
      // This will be handled by the AudioBackend component via _lastMessage
      break;
      
    case 'server_shutdown':
      console.log('Server is shutting down, closing window');
      // Close the current window/tab when server shuts down
      window.close();
      // If window.close() doesn't work (some browsers restrict it), update the UI
      appState.update(state => ({
        ...state,
        connected: false,
        error: 'Server has stopped. Please restart the server to continue.'
      }));
      break;
      
    default:
      console.log('Unhandled message type:', type, message);
  }
}

/**
 * Send message to WebSocket server
 */
export function sendMessage(message) {
  // Add debugging for REAPER reset functionality
  if (message.type === 'reinit_reaper_with_backup') {
    console.log('SENDING REAPER RESET MESSAGE:', message);
  }
  
  if (socket && socket.readyState === WebSocket.OPEN) {
    const messageStr = JSON.stringify(message);
    socket.send(messageStr);
    
    // Log after sending
    if (message.type === 'reinit_reaper_with_backup') {
      console.log('REAPER RESET MESSAGE SENT SUCCESSFULLY');
    }
    
    return true;
  }
  
  console.warn('WebSocket not connected, unable to send message:', message);
  return false;
}

/**
 * Increment counter
 */
export function incrementCounter() {
  return sendMessage({
    type: 'increment_counter'
  });
}

/**
 * Fallback REST API for browsers without WebSocket support
 */
export async function incrementCounterFallback() {
  try {
    const response = await fetch('/api/increment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    const data = await response.json();
    
    // Update store manually since we're not getting WebSocket updates
    appState.update(state => ({
      ...state,
      counter: data.counter,
      welcomeText: data.welcome_text
    }));
    
    return true;
  } catch (error) {
    console.error('Error incrementing counter:', error);
    
    appState.update(state => ({
      ...state,
      error: 'Failed to increment counter. Please try again.'
    }));
    
    return false;
  }
}