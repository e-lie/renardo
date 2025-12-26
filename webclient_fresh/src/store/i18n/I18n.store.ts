import { writable, derived, get } from 'svelte/store'
import { translations, type Language, type TranslationKey } from '../../i18n/translations'

interface I18nState {
  currentLanguage: Language
}

// Initialize from localStorage if available
let initialLanguage: Language = 'en'
if (typeof localStorage !== 'undefined') {
  const savedLang = localStorage.getItem('renardo-language') as Language | null
  if (savedLang && (savedLang === 'en' || savedLang === 'fr' || savedLang === 'es' || savedLang === 'de')) {
    initialLanguage = savedLang
  }
}

const initialState: I18nState = {
  currentLanguage: initialLanguage
}

const writableI18nStore = writable<I18nState>(initialState)

const actions = {
  setLanguage: (lang: Language) => {
    writableI18nStore.update(state => ({ ...state, currentLanguage: lang }))
    // Persist to localStorage
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('renardo-language', lang)
    }
  }
}

const getters = {
  currentLanguage: derived(writableI18nStore, $state => $state.currentLanguage),
  translate: derived(writableI18nStore, $state => {
    return (key: TranslationKey): string => {
      return translations[$state.currentLanguage][key]
    }
  })
}

export function useI18nStore() {
  return { actions, getters }
}
