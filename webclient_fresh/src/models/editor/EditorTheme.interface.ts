export interface EditorThemeInterface {
  name: string
  value: string
}

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
