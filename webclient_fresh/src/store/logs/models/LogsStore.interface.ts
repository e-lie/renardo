import type { Readable } from 'svelte/store'
import type { LogEntryInterface } from '../../../models/logs'

export interface LogsStoreActionsInterface {
  loadLogs: (limit?: number) => Promise<void>
  setFilterLevel: (level: string | null) => void
  subscribeToLogs: () => void
  unsubscribeFromLogs: () => void
}

export interface LogsStoreGettersInterface {
  loading: Readable<boolean>
  logs: Readable<LogEntryInterface[]>
  filterLevel: Readable<string | null>
  filteredLogs: Readable<LogEntryInterface[]>
}

export interface LogsStoreInterface {
  actions: LogsStoreActionsInterface
  getters: LogsStoreGettersInterface
}
