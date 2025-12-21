import { writable, derived } from 'svelte/store'
import { apiClient } from '../../api-client/rest/api'
import type { TutorialFileInterface, TutorialLanguageInterface } from '@/models/tutorial'
import type {
  TutorialStateInterface,
  TutorialStoreInterface,
  TutorialStoreActionsInterface,
  TutorialStoreGettersInterface
} from './models'

// Private writable store
const writableTutorialStore = writable<TutorialStateInterface>({
  loading: false,
  languages: {},
  selectedLanguage: null,
  tutorialFiles: [],
  error: null
})

// Public hook
export function useTutorialStore(): TutorialStoreInterface {
  // Actions: modify state
  const actions: TutorialStoreActionsInterface = {
    loadTutorialFiles: async (language?: string) => {
      writableTutorialStore.update(state => ({ ...state, loading: true, error: null }))
      
      try {
        const url = language ? `/api/tutorial/files?lang=${language}` : '/api/tutorial/files'
        const response = await apiClient.get(url)
        
        if (response.data?.success) {
          const languages = response.data.languages
          const availableLanguages = Object.keys(languages)
          
          writableTutorialStore.update(state => ({
            ...state,
            languages,
            tutorialFiles: language && languages[language] ? languages[language] : [],
            selectedLanguage: language && availableLanguages.includes(language) ? language : null,
            loading: false
          }))
        } else {
          throw new Error('Failed to load tutorial files')
        }
      } catch (error) {
        writableTutorialStore.update(state => ({
          ...state,
          error: error instanceof Error ? error.message : 'Unknown error',
          loading: false
        }))
      }
    },

    selectLanguage: (language: string) => {
      writableTutorialStore.update(state => {
        const tutorialFiles = state.languages[language] || []
        return {
          ...state,
          selectedLanguage: language,
          tutorialFiles,
          error: null
        }
      })
    },

    selectTutorialFile: async (file: TutorialFileInterface) => {
      try {
        const response = await apiClient.get(file.url)
        
        if (response.data) {
          // Here you would integrate with the editor store to load the content
          // For now, we'll just log the content
          console.log('Tutorial content loaded:', response.data)
        }
      } catch (error) {
        writableTutorialStore.update(state => ({
          ...state,
          error: error instanceof Error ? error.message : 'Failed to load tutorial content'
        }))
      }
    },

    setError: (error: string | null) => {
      writableTutorialStore.update(state => ({ ...state, error }))
    }
  }

  // Getters: read-only derived stores
  const loading = derived(writableTutorialStore, $state => $state.loading)
  const languages = derived(writableTutorialStore, $state => $state.languages)
  const selectedLanguage = derived(writableTutorialStore, $state => $state.selectedLanguage)
  const tutorialFiles = derived(writableTutorialStore, $state => $state.tutorialFiles)
  const error = derived(writableTutorialStore, $state => $state.error)
  
  const availableLanguages = derived(writableTutorialStore, $state => 
    Object.keys($state.languages)
  )

  const getters: TutorialStoreGettersInterface = {
    loading,
    languages,
    selectedLanguage,
    tutorialFiles,
    error,
    availableLanguages
  }

  return { actions, getters }
}