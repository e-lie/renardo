import { writable } from 'svelte/store'
import { useTutorialStore } from '../tutorial/Tutorial.store'
import { useWebSocketBackendStore } from '../websocket/WebSocketBackend.store'
import type { RootStoreInterface } from './models'

// Router store for navigation
export const currentPage = writable<'editor'>('editor')

// Hook that returns our root store instance
export function useAppStore(): RootStoreInterface {
  const tutorialStore = useTutorialStore()
  const webSocketBackendStore = useWebSocketBackendStore()

  return {
    tutorialStore,
    webSocketBackendStore
  }
}
