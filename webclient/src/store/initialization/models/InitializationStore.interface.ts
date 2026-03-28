import type { Readable } from 'svelte/store'
import type { InitLogEntry } from './InitializationState.interface'

export interface InitializationStoreActionsInterface {
  checkStatus: () => Promise<void>
  downloadMissing: (downloadSamples: boolean, downloadSccode: boolean) => Promise<void>
  clearLogs: () => void
  subscribeToWebSocket: (wsStore: any) => void
}

export interface InitializationStoreGettersInterface {
  loading: Readable<boolean>
  userDirConfigured: Readable<boolean>
  userDir: Readable<string | null>
  samplesInitialized: Readable<boolean>
  sccodeInitialized: Readable<boolean>
  downloading: Readable<boolean>
  downloadComplete: Readable<boolean>
  downloadError: Readable<string | null>
  initLogs: Readable<InitLogEntry[]>
  hasAllResources: Readable<boolean>
}

export interface InitializationStoreInterface {
  actions: InitializationStoreActionsInterface
  getters: InitializationStoreGettersInterface
}
