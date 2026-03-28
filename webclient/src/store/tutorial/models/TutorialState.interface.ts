import type { TutorialFileInterface, TutorialLanguageInterface } from '@/models/tutorial'

export interface TutorialStateInterface {
  loading: boolean
  languages: TutorialLanguageInterface
  selectedLanguage: string | null
  tutorialFiles: TutorialFileInterface[]
  error: string | null
}