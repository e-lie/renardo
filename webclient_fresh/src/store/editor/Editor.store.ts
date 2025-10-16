import { writable, derived } from 'svelte/store'
import type {
  EditorStateInterface,
  EditorStoreInterface,
  EditorStoreActionsInterface,
  EditorStoreGettersInterface
} from './models'

// Private writable store
const writableEditorStore = writable<EditorStateInterface>({
  currentSession: 'renardo-session'
})

// Public hook
export function useEditorStore(): EditorStoreInterface {
  // Actions: modify state
  const actions: EditorStoreActionsInterface = {
    setCurrentSession: (sessionName: string) => {
      writableEditorStore.update(state => ({ ...state, currentSession: sessionName }))
    }
  }

  // Getters: read-only derived stores
  const currentSession = derived(writableEditorStore, $state => $state.currentSession)

  const getters: EditorStoreGettersInterface = {
    currentSession
  }

  return { actions, getters }
}
