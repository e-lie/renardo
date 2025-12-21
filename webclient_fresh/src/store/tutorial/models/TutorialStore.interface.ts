import type { Readable } from 'svelte/store'
import type { TutorialFileInterface, TutorialLanguageInterface } from '@/models/tutorial'

export interface TutorialStoreActionsInterface {
  loadTutorialFiles: (language?: string) => Promise<void>
  selectLanguage: (language: string) => void
  selectTutorialFile: (file: TutorialFileInterface) => Promise<void>
  setError: (error: string | null) => void
}

export interface TutorialStoreGettersInterface {
  loading: Readable<boolean>
  languages: Readable<TutorialLanguageInterface>
  selectedLanguage: Readable<string | null>
  tutorialFiles: Readable<TutorialFileInterface[]>
  error: Readable<string | null>
  availableLanguages: Readable<string[]>
}

export interface TutorialStoreInterface {
  actions: TutorialStoreActionsInterface
  getters: TutorialStoreGettersInterface
}