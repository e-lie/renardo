import { writable, derived } from 'svelte/store'
import type {
  WebSocketBackendStateInterface,
  WebSocketBackendStoreInterface,
  WebSocketBackendStoreActionsInterface,
  WebSocketBackendStoreGettersInterface,
  ConsoleMessageInterface,
  WebSocketMessageInterface,
  WebSocketCommandInterface
} from '../../models/websocket'

// Helper function to generate unique IDs
function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// Initial state
const initialState: WebSocketBackendStateInterface = {
  connectionStatus: 'disconnected',
  consoleMessages: [],
  error: null
}

// Private writable store
const writableWebSocketStore = writable<WebSocketBackendStateInterface>(initialState)

// WebSocket instance
let ws: WebSocket | null = null
let reconnectAttempts = 0
const maxReconnectAttempts = 5
const reconnectDelay = 3000

// WebSocket connection function
function connectWebSocket() {
  if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) {
    return
  }

  writableWebSocketStore.update(state => ({ ...state, connectionStatus: 'connecting' }))

  try {
    const wsUrl = `ws://localhost:8000/ws/ws`
    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected')
      reconnectAttempts = 0
      writableWebSocketStore.update(state => ({ 
        ...state, 
        connectionStatus: 'connected',
        error: null 
      }))

      // Start heartbeat
      startHeartbeat()
    }

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessageInterface = JSON.parse(event.data)
        handleWebSocketMessage(message)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      writableWebSocketStore.update(state => ({ ...state, connectionStatus: 'disconnected' }))
      ws = null
      stopHeartbeat()

      // Attempt reconnection
      if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++
        console.log(`Attempting reconnection ${reconnectAttempts}/${maxReconnectAttempts}...`)
        setTimeout(connectWebSocket, reconnectDelay)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      writableWebSocketStore.update(state => ({ 
        ...state, 
        connectionStatus: 'error',
        error: 'WebSocket connection error'
      }))
    }

  } catch (error) {
    writableWebSocketStore.update(state => ({ 
      ...state, 
      connectionStatus: 'error',
      error: 'Failed to create WebSocket connection'
    }))
  }
}

// Heartbeat mechanism
let heartbeatInterval: number | null = null

function startHeartbeat() {
  heartbeatInterval = window.setInterval(() => {
    sendWebSocketMessage({
      type: 'ping',
      data: null,
      timestamp: new Date().toISOString()
    })
  }, 30000) // 30 seconds
}

function stopHeartbeat() {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval)
    heartbeatInterval = null
  }
}

// Send message through WebSocket
function sendWebSocketMessage(message: WebSocketMessageInterface) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message))
  } else {
    console.warn('WebSocket not connected, cannot send message:', message)
  }
}

// Handle incoming WebSocket messages
function handleWebSocketMessage(message: WebSocketMessageInterface) {
  switch (message.type) {
    case 'console_message':
      handleConsoleMessage(message.data)
      break
    case 'command_response':
      // Handle command responses if needed
      break
    case 'error':
      writableWebSocketStore.update(state => ({ 
        ...state, 
        error: message.data.message || 'Unknown backend error'
      }))
      break
    case 'pong':
      // Heartbeat response, no action needed
      break
    default:
      console.warn('Unknown WebSocket message type:', message.type)
  }
}

// Handle console messages from backend
function handleConsoleMessage(data: any) {
  const consoleMessage: ConsoleMessageInterface = {
    id: generateId(),
    timestamp: new Date(data.timestamp),
    level: data.level || 'info',
    source: data.source || 'backend',
    message: data.message,
    metadata: data.metadata
  }

  writableWebSocketStore.update(state => ({
    ...state,
    consoleMessages: [...state.consoleMessages, consoleMessage]
  }))
}

// Public hook
export function useWebSocketBackendStore(): WebSocketBackendStoreInterface {
  // Actions: modify state
  const actions: WebSocketBackendStoreActionsInterface = {
    connect: () => {
      connectWebSocket()
    },

    disconnect: () => {
      stopHeartbeat()
      if (ws) {
        ws.close()
        ws = null
      }
      writableWebSocketStore.update(state => ({ 
        ...state, 
        connectionStatus: 'disconnected',
        error: null 
      }))
    },

    sendCommand: (command: WebSocketCommandInterface) => {
      sendWebSocketMessage({
        type: 'command_response',
        data: command,
        timestamp: new Date().toISOString()
      })
    },

    clearError: () => {
      writableWebSocketStore.update(state => ({ ...state, error: null }))
    }
  }

  // Getters: read-only derived stores
  const connectionStatus = derived(writableWebSocketStore, $state => $state.connectionStatus)
  const consoleMessages = derived(writableWebSocketStore, $state => $state.consoleMessages)
  const error = derived(writableWebSocketStore, $state => $state.error)
  const isConnected = derived(connectionStatus, $status => $status === 'connected')

  const getters: WebSocketBackendStoreGettersInterface = {
    connectionStatus,
    consoleMessages,
    error,
    isConnected
  }

  return { actions, getters }
}