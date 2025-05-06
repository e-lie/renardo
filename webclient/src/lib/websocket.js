import { writable } from 'svelte/store';

// Create stores for application state
export const appState = writable({
  counter: 0,
  welcomeText: 'Loading...',
  connected: false,
  error: null
});

// WebSocket connection
let socket;
let reconnectTimer;
const MAX_RECONNECT_DELAY = 5000;
let reconnectAttempts = 0;

/**
 * Initialize WebSocket connection
 */
export function initWebSocket() {
  // Close any existing connection
  if (socket) {
    socket.close();
  }

  // Clear any reconnect timer
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
  }
  
  // Determine WebSocket URL based on current location
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = import.meta.env.DEV 
    ? 'ws://localhost:5000/ws'  // Development
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
  });
  
  // Connection closed
  socket.addEventListener('close', (event) => {
    console.log('WebSocket connection closed', event);
    
    // Update store to indicate disconnected status
    appState.update(state => ({
      ...state,
      connected: false
    }));
    
    // Attempt to reconnect with exponential backoff
    const delay = Math.min(1000 * Math.pow(1.5, reconnectAttempts), MAX_RECONNECT_DELAY);
    reconnectAttempts++;
    
    console.log(`Attempting to reconnect in ${delay}ms...`);
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
  const { type, data, error } = message;
  
  switch (type) {
    case 'initial_state':
    case 'state_updated':
      // Update application state
      appState.update(state => ({
        ...state,
        counter: data.counter,
        welcomeText: data.welcome_text,
        error: null
      }));
      break;
      
    case 'error':
      // Handle error message
      console.error('Server error:', error);
      appState.update(state => ({
        ...state,
        error: error || 'Unknown server error'
      }));
      break;
      
    default:
      console.log('Unhandled message type:', type);
  }
}

/**
 * Send message to WebSocket server
 */
export function sendMessage(message) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
    return true;
  }
  
  console.warn('WebSocket not connected, unable to send message');
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