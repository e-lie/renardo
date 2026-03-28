export interface WebSocketBackendStateInterface {
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error'
  consoleMessages: ConsoleMessageInterface[]
  error: string | null
}

export interface WebSocketBackendStoreInterface {
  actions: WebSocketBackendStoreActionsInterface
  getters: WebSocketBackendStoreGettersInterface
}

export interface WebSocketBackendStoreActionsInterface {
  connect: () => void
  disconnect: () => void
  sendCommand: (command: any) => void
  clearError: () => void
}

export interface WebSocketBackendStoreGettersInterface {
  connectionStatus: import('svelte/store').Readable<'disconnected' | 'connecting' | 'connected' | 'error'>
  consoleMessages: import('svelte/store').Readable<ConsoleMessageInterface[]>
  error: import('svelte/store').Readable<string | null>
  isConnected: import('svelte/store').Readable<boolean>
}

export interface ConsoleMessageInterface {
  id: string
  timestamp: Date
  level: 'info' | 'warning' | 'error' | 'debug'
  source: 'backend' | 'runtime' | 'system'
  message: string
  metadata?: Record<string, any>
}

export interface WebSocketMessageInterface {
  type: 'console_message' | 'command_response' | 'error' | 'ping' | 'pong'
  data: any
  timestamp: string
}

export interface WebSocketCommandInterface {
  type: 'execute_code' | 'get_state' | 'ping'
  data?: any
}