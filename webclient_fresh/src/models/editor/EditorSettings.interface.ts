/**
 * Editor settings interface
 */
export interface EditorSettingsInterface {
    theme: 'light' | 'dark' | 'oneDark' | 'dracula'
    fontSize: number
    fontFamily: string
    tabSize: number
    showLineNumbers: boolean
    lineWrapping: boolean
    vimMode: boolean
}
