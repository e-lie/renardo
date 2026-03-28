import type { DirectoryEntry } from '@/models/file-explorer'

export interface UserDirectoryStateInterface {
  loading: boolean
  userDirectoryPath: string | null
  currentPath: string | null
  entries: DirectoryEntry[]
  error: string | null
}
