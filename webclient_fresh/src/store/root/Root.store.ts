import { writable } from 'svelte/store'
import { useTutorialStore } from '../tutorial/Tutorial.store'
import type { RootStoreInterface } from './models'

// Router store for navigation
export const currentPage = writable<'editor'>('editor')

// Hook that returns our root store instance
export function useAppStore(): RootStoreInterface {
  const tutorialStore = useTutorialStore()

  return {
    tutorialStore
  }
}
