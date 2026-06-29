import type { Readable } from 'svelte/store'
import type { AbletonStatusInterface } from './AbletonState.interface'

export interface AbletonStoreActionsInterface {
  loadStatus: () => Promise<void>
  start: () => Promise<void>
  stop: () => Promise<void>
  restart: () => Promise<void>
  loadStartupEnabled: () => Promise<void>
  setStartupEnabled: (enabled: boolean) => Promise<void>
  clearError: () => void
}

export interface AbletonStoreGettersInterface {
  status: Readable<AbletonStatusInterface>
  startupEnabled: Readable<boolean>
  isLoading: Readable<boolean>
  error: Readable<string | null>
}

export interface AbletonStoreInterface {
  actions: AbletonStoreActionsInterface
  getters: AbletonStoreGettersInterface
}
