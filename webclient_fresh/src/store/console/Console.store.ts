import { writable, derived } from 'svelte/store'
import type { ConsoleMessageInterface } from '../../models/console'
import type {
  ConsoleStateInterface,
  ConsoleStoreInterface,
  ConsoleStoreActionsInterface,
  ConsoleStoreGettersInterface
} from './models'

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

  // Getters
  const messages = derived(writableConsoleStore, $state => $state.messages)
  const isMinimized = derived(writableConsoleStore, $state => $state.isMinimized)

  const getters: ConsoleStoreGettersInterface = {
    messages,
    isMinimized
  }

  return { actions, getters }
}
