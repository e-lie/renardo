import { writable, derived } from 'svelte/store'
import { apiClient } from '../../api-client/rest/api'
import { dispatchLoadFile } from '../../events/editorEvents'
import type { MusicExampleFileInterface } from '../../models/music-example'
import type {
  MusicExampleStateInterface,
  MusicExampleStoreInterface,
  MusicExampleStoreActionsInterface,
  MusicExampleStoreGettersInterface
} from './models'

// Private writable store
const writableMusicExampleStore = writable<MusicExampleStateInterface>({
  loading: false,
  musicExampleFiles: [],
  error: null
})

// Public hook
export function useMusicExampleStore(): MusicExampleStoreInterface {
  // Actions: modify state
  const actions: MusicExampleStoreActionsInterface = {
    loadMusicExampleFiles: async () => {
      writableMusicExampleStore.update(state => ({ ...state, loading: true, error: null }))

      try {
        const url = '/api/music-examples/files'
        console.log('Loading music examples from:', url)
        const response = await apiClient.get(url)
        console.log('API response:', response)

        if (response?.success) {
          const files = response.files

          writableMusicExampleStore.update(state => ({
            ...state,
            musicExampleFiles: files,
            loading: false
          }))
        } else {
          throw new Error('Failed to load music example files')
        }
      } catch (error) {
        console.error('Error loading music example files:', error)
        writableMusicExampleStore.update(state => ({
          ...state,
          error: error instanceof Error ? error.message : 'Unknown error',
          loading: false
        }))
      }
    },

    selectMusicExampleFile: async (file: MusicExampleFileInterface) => {
      try {
        const response = await fetch(`http://localhost:8000${file.url}`)

        if (response.ok) {
          const content = await response.text()
          dispatchLoadFile(content, file.name.replace('.py', ''), file.path)
        } else {
          throw new Error('Failed to load music example file')
        }
      } catch (error) {
        writableMusicExampleStore.update(state => ({
          ...state,
          error: error instanceof Error ? error.message : 'Failed to load music example content'
        }))
      }
    },

    setError: (error: string | null) => {
      writableMusicExampleStore.update(state => ({ ...state, error }))
    }
  }

  // Getters: read-only derived stores
  const loading = derived(writableMusicExampleStore, $state => $state.loading)
  const musicExampleFiles = derived(writableMusicExampleStore, $state => $state.musicExampleFiles)
  const error = derived(writableMusicExampleStore, $state => $state.error)

  const getters: MusicExampleStoreGettersInterface = {
    loading,
    musicExampleFiles,
    error
  }

  return { actions, getters }
}
