import { writable } from 'svelte/store'
import { useTutorialStore } from '../tutorial/Tutorial.store'
import { useMusicExampleStore } from '../music-example/MusicExample.store'
import { useUserDirectoryStore } from '../user-directory/UserDirectory.store'
import { useWebSocketBackendStore } from '../websocket/WebSocketBackend.store'
import type { RootStoreInterface } from './models'

// Router store for navigation
export const currentPage = writable<'editor'>('editor')

// Hook that returns our root store instance
export function useAppStore(): RootStoreInterface {
  const tutorialStore = useTutorialStore()
  const musicExampleStore = useMusicExampleStore()
  const userDirectoryStore = useUserDirectoryStore()
  const webSocketBackendStore = useWebSocketBackendStore()

  return {
    tutorialStore,
    musicExampleStore,
    userDirectoryStore,
    webSocketBackendStore
  }
}
