/**
 * Available theme definition
 */
export interface EditorThemeInterface {
  name: string
  value: string
}

/**
 * List of available themes
 */
export const AVAILABLE_THEMES: EditorThemeInterface[] = [
  { name: 'Monokai', value: 'monokai' },
  { name: 'Dracula', value: 'dracula' },
  { name: 'Material', value: 'material' },
  { name: 'Nord', value: 'nord' },
  { name: 'Solarized Dark', value: 'solarized-dark' },
  { name: 'Solarized Light', value: 'solarized-light' },
  { name: 'Darcula', value: 'darcula' },
  { name: 'Eclipse', value: 'eclipse' },
]

/**
 * Editor settings interface
 */
export interface EditorSettingsInterface {
    theme: 'monokai' | 'dracula' | 'material' | 'nord' | 'solarized-dark' | 'solarized-light' | 'darcula' | 'eclipse'
    fontSize: number
    lineHeight: number
    fontFamily: string
    tabSize: number
    showLineNumbers: boolean
    lineWrapping: boolean
    vimMode: boolean
}
