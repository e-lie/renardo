import type { Readable } from 'svelte/store'
import type { ConsoleMessageInterface } from '../../../models/console'

export interface ConsoleStoreActionsInterface {
  addMessage: (message: ConsoleMessageInterface) => void
  clearMessages: () => void
  toggleMinimize: () => void
  setMinimized: (minimized: boolean) => void
}

export interface ConsoleStoreGettersInterface {
  messages: Readable<ConsoleMessageInterface[]>
  isMinimized: Readable<boolean>
}

export interface ConsoleStoreInterface {
  actions: ConsoleStoreActionsInterface
  getters: ConsoleStoreGettersInterface
  syncWithWebSocket?: (webSocketStore: any) => (() => void) | undefined
}
