import type { Readable } from 'svelte/store'

export interface EditorStoreActionsInterface {
  setCurrentSession: (sessionName: string) => void
}

export interface EditorStoreGettersInterface {
  currentSession: Readable<string>
}

export interface EditorStoreInterface {
  actions: EditorStoreActionsInterface
  getters: EditorStoreGettersInterface
}
