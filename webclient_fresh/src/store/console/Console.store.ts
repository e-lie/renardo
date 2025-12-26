import { writable, derived, get } from 'svelte/store'
import type { ConsoleMessageInterface } from '../../models/console'
import type {
  ConsoleStateInterface,
  ConsoleStoreInterface,
  ConsoleStoreActionsInterface,
  ConsoleStoreGettersInterface
} from './models'
import type { ConsoleMessageInterface as WebSocketConsoleMessageInterface } from '../../models/websocket'

// Initial state
const initialState: ConsoleStateInterface = {
  messages: [],
  isMinimized: false
}

// Private writable store
const writableConsoleStore = writable<ConsoleStateInterface>(initialState)

// Public hook
export function useConsoleStore(): ConsoleStoreInterface {
  // Actions
  const actions: ConsoleStoreActionsInterface = {
    addMessage: (message: ConsoleMessageInterface) => {
      writableConsoleStore.update(state => ({
        ...state,
        messages: [...state.messages, message]
      }))
    },

    clearMessages: () => {
      writableConsoleStore.update(state => ({
        ...state,
        messages: []
      }))
    },

    toggleMinimize: () => {
      writableConsoleStore.update(state => ({
        ...state,
        isMinimized: !state.isMinimized
      }))
    },

    setMinimized: (minimized: boolean) => {
      writableConsoleStore.update(state => ({
        ...state,
        isMinimized: minimized
      }))
    }
  }

  // Sync with WebSocket messages
  const syncWithWebSocket = (webSocketStore: any) => {
    if (!webSocketStore) return

    // Subscribe to WebSocket console messages
    const unsubscribe = webSocketStore.getters.consoleMessages.subscribe((wsMessages: WebSocketConsoleMessageInterface[]) => {
      wsMessages.forEach((wsMessage: WebSocketConsoleMessageInterface) => {
        // Convert WebSocket message to Console message format
        const consoleMessage: ConsoleMessageInterface = {
          id: wsMessage.id,
          timestamp: wsMessage.timestamp,
          level: wsMessage.level as 'info' | 'warning' | 'error' | 'debug',
          message: `[${wsMessage.source}] ${wsMessage.message}`,
          metadata: wsMessage.metadata
        }

        // Add to console if not already present
        writableConsoleStore.update(state => {
          const messageExists = state.messages.some(msg => msg.id === consoleMessage.id)
          if (messageExists) return state
          
          return {
            ...state,
            messages: [...state.messages, consoleMessage]
          }
        })
      })
    })

    return unsubscribe
  }

  // Getters
  const messages = derived(writableConsoleStore, $state => $state.messages)
  const isMinimized = derived(writableConsoleStore, $state => $state.isMinimized)

  const getters: ConsoleStoreGettersInterface = {
    messages,
    isMinimized
  }

  return { actions, getters, syncWithWebSocket }
}
