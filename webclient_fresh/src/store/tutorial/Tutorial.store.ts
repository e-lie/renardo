import { writable, derived } from 'svelte/store'
import { apiClient } from '../../api-client/rest/api'
import type { TutorialFileInterface, TutorialLanguageInterface } from '../../models/tutorial'
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
        console.log('Loading tutorials from:', url)
        const response = await apiClient.get(url)
        console.log('API response:', response)
        
        if (response?.success) {
          const languages = response.languages
          const availableLanguages = Object.keys(languages)
          console.log('Available languages:', availableLanguages)

          // Default to 'en' if available and no language specified
          const defaultLang = language || (availableLanguages.includes('en') ? 'en' : availableLanguages[0])

          writableTutorialStore.update(state => ({
            ...state,
            languages,
            tutorialFiles: defaultLang && languages[defaultLang] ? languages[defaultLang] : [],
            selectedLanguage: defaultLang || null,
            loading: false
          }))
        } else {
          throw new Error('Failed to load tutorial files')
        }
      } catch (error) {
        console.error('Error loading tutorial files:', error)
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

    selectTutorialFile: async (file: TutorialFileInterface, editorStore: any) => {
      try {
        const response = await fetch(`http://localhost:8000${file.url}`)

        if (response.ok) {
          const content = await response.text()
          // Load content in editor
          if (editorStore?.actions?.loadContentInNewTab) {
            editorStore.actions.loadContentInNewTab(content, file.name.replace('.py', ''))
          }
        } else {
          throw new Error('Failed to load tutorial file')
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