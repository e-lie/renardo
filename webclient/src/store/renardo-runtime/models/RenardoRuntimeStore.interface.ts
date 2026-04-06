import type { Readable } from 'svelte/store'
import type { RenardoRuntimeStatusInterface } from './RenardoRuntimeState.interface'
import type { ConsoleMessageInterface } from '../../../models/websocket/WebSocketBackend.interface'

export interface RenardoRuntimeStoreActionsInterface {
  loadStatus: () => Promise<void>
  startRuntime: () => Promise<void>
  stopRuntime: () => Promise<void>
  restartRuntime: () => Promise<void>
  clearError: () => void
}

export interface RenardoRuntimeStoreGettersInterface {
  status: Readable<RenardoRuntimeStatusInterface>
  isLoading: Readable<boolean>
  error: Readable<string | null>
  runtimeLogs: Readable<ConsoleMessageInterface[]>
}

export interface RenardoRuntimeStoreInterface {
  actions: RenardoRuntimeStoreActionsInterface
  getters: RenardoRuntimeStoreGettersInterface
}
