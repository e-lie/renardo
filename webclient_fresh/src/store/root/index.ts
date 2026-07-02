import { writable } from 'svelte/store'
import { useEditorStore } from '../editor/Editor.store'
import { useLayoutStore } from '../layout/Layout.store'

export function useAppStore() {
  const editorStore = useEditorStore()
  const layoutStore = useLayoutStore()

  return {
    editorStore,
    layoutStore
  }
}

export const currentPage = writable<'editor' | 'settings'>('editor')

export * from './Root.store'
export * from './models'
