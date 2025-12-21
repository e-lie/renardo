export interface TutorialFileInterface {
  name: string
  path: string
  url: string
}

export interface TutorialLanguageInterface {
  [languageCode: string]: TutorialFileInterface[]
}

export interface TutorialResponseInterface {
  success: boolean
  languages: TutorialLanguageInterface
}