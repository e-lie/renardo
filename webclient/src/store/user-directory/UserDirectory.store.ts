import { writable, derived } from 'svelte/store'
import { apiClient } from '../../api-client/rest/api'
import type { DirectoryEntry } from '../../models/file-explorer'
import type {
  UserDirectoryStateInterface,
  UserDirectoryStoreInterface,
  UserDirectoryStoreActionsInterface,
  UserDirectoryStoreGettersInterface
} from './models'

// Private writable store
const writableUserDirectoryStore = writable<UserDirectoryStateInterface>({
  loading: false,
  userDirectoryPath: null,
  currentPath: null,
  entries: [],
  error: null
})

// Public hook
export function useUserDirectoryStore(): UserDirectoryStoreInterface {
  // Actions: modify state
  const actions: UserDirectoryStoreActionsInterface = {
    loadUserDirectory: async () => {
      writableUserDirectoryStore.update(state => ({ ...state, loading: true, error: null }))

      try {
        const response = await apiClient.get('/api/user-directory')
        console.log('User directory response:', response)

        if (response?.success) {
          writableUserDirectoryStore.update(state => ({
            ...state,
            userDirectoryPath: response.path,
            currentPath: response.path,
            loading: false
          }))

          // Load directory contents
          await actions.listUserDirectory()
        } else {
          throw new Error('Failed to load user directory')
        }
      } catch (error) {
        console.error('Error loading user directory:', error)
        writableUserDirectoryStore.update(state => ({
          ...state,
          error: error instanceof Error ? error.message : 'Unknown error',
          loading: false
        }))
      }
    },

    listUserDirectory: async (subpath?: string) => {
      writableUserDirectoryStore.update(state => ({ ...state, loading: true, error: null }))

      try {
        const url = subpath ? `/api/user-directory/list?subpath=${encodeURIComponent(subpath)}` : '/api/user-directory/list'
        const response = await apiClient.get(url)
        console.log('List user directory response:', response)

        if (response?.success) {
          writableUserDirectoryStore.update(state => ({
            ...state,
            entries: response.entries || [],
            currentPath: response.current_path,
            loading: false
          }))
        } else {
          throw new Error('Failed to list user directory')
        }
      } catch (error) {
        console.error('Error listing user directory:', error)
        writableUserDirectoryStore.update(state => ({
          ...state,
          error: error instanceof Error ? error.message : 'Unknown error',
          loading: false
        }))
      }
    },

    setUserDirectory: async (path: string) => {
      writableUserDirectoryStore.update(state => ({ ...state, loading: true, error: null }))

      try {
        const response = await apiClient.post('/api/user-directory/set', { path })
        console.log('Set user directory response:', response)

        if (response?.success) {
          writableUserDirectoryStore.update(state => ({
            ...state,
            userDirectoryPath: response.path,
            currentPath: response.path,
            loading: false
          }))

          // Reload directory contents
          await actions.listUserDirectory()
        } else {
          throw new Error('Failed to set user directory')
        }
      } catch (error) {
        console.error('Error setting user directory:', error)
        writableUserDirectoryStore.update(state => ({
          ...state,
          error: error instanceof Error ? error.message : 'Unknown error',
          loading: false
        }))
      }
    },

    navigateToEntry: async (entry: DirectoryEntry) => {
      if (entry.type === 'directory') {
        // Navigate to subdirectory
        const state = writableUserDirectoryStore
        const currentState = await new Promise<UserDirectoryStateInterface>((resolve) => {
          const unsubscribe = state.subscribe(value => {
            resolve(value)
            unsubscribe()
          })
        })

        const userDir = currentState.userDirectoryPath
        const currentPath = currentState.currentPath

        if (userDir && currentPath) {
          // Calculate relative path from user directory
          const relativePath = entry.path.replace(userDir, '').replace(/^\//, '')
          await actions.listUserDirectory(relativePath)
        }
      } else if (entry.type === 'file') {
        // Handle file click (could load in editor, etc.)
        console.log('File clicked:', entry.path)
      }
    },

    setError: (error: string | null) => {
      writableUserDirectoryStore.update(state => ({ ...state, error }))
    }
  }

  // Getters: read-only derived stores
  const loading = derived(writableUserDirectoryStore, $state => $state.loading)
  const userDirectoryPath = derived(writableUserDirectoryStore, $state => $state.userDirectoryPath)
  const currentPath = derived(writableUserDirectoryStore, $state => $state.currentPath)
  const entries = derived(writableUserDirectoryStore, $state => $state.entries)
  const error = derived(writableUserDirectoryStore, $state => $state.error)

  const getters: UserDirectoryStoreGettersInterface = {
    loading,
    userDirectoryPath,
    currentPath,
    entries,
    error
  }

  return { actions, getters }
}
