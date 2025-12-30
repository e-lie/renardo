import type { Readable } from 'svelte/store'
import type { DirectoryEntry } from '@/models/file-explorer'

export interface UserDirectoryStoreActionsInterface {
  loadUserDirectory: () => Promise<void>
  listUserDirectory: (subpath?: string) => Promise<void>
  setUserDirectory: (path: string) => Promise<void>
  navigateToEntry: (entry: DirectoryEntry) => Promise<void>
  setError: (error: string | null) => void
}

export interface UserDirectoryStoreGettersInterface {
  loading: Readable<boolean>
  userDirectoryPath: Readable<string | null>
  currentPath: Readable<string | null>
  entries: Readable<DirectoryEntry[]>
  error: Readable<string | null>
}

export interface UserDirectoryStoreInterface {
  actions: UserDirectoryStoreActionsInterface
  getters: UserDirectoryStoreGettersInterface
}
