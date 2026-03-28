import type { DirectoryEntry } from '../file-explorer'

export interface UserDirectoryResponseInterface {
  success: boolean
  path: string
}

export interface UserDirectoryListResponseInterface {
  success: boolean
  entries: DirectoryEntry[]
  current_path: string
}

export interface SetUserDirectoryRequestInterface {
  path: string
}
