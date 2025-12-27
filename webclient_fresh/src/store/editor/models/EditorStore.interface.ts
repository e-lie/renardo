import type { Readable } from 'svelte/store'
import type { BufferInterface, TabInterface, EditorSettingsInterface, CreateBufferOptions, CreateTabOptions, EditorInstance } from '../../../models/editor'

/**
 * Editor store actions interface
 */
export interface EditorStoreActionsInterface {
    // Editor management
    registerEditor: (componentId: string) => string
    unregisterEditor: (editorId: string) => void

    // Buffer actions
    createBuffer: (options: CreateBufferOptions) => string
    updateBufferContent: (bufferId: string, content: string) => void
    saveBuffer: (bufferId: string, filePath: string) => Promise<{ success: boolean; message: string }>
    renameBuffer: (bufferId: string, newName: string) => void

    // Tab actions (now require editorId)
    createTab: (editorId: string, bufferId: string, title?: string) => string
    loadContentInNewTab: (editorId: string, content: string, title: string, filePath?: string) => string
    switchToTab: (editorId: string, tabId: string) => void
    closeTab: (editorId: string, tabId: string) => void
    updateTabTitle: (tabId: string, newTitle: string) => void

    // Settings and execution
    updateSettings: (settings: Partial<EditorSettingsInterface>) => void
    executeCode: (code: string) => Promise<{ success: boolean; message: string }>
}

/**
 * Editor store getters interface
 */
export interface EditorStoreGettersInterface {
    // Global getters
    tabs: Readable<TabInterface[]>
    buffers: Readable<BufferInterface[]>
    settings: Readable<EditorSettingsInterface>
    startupBuffer: Readable<BufferInterface | null>

    // Editor-specific getters (functions)
    getEditor: (editorId: string) => Readable<EditorInstance | null>
    getEditorTabs: (editorId: string) => Readable<TabInterface[]>
    getEditorActiveTab: (editorId: string) => Readable<TabInterface | null>
    getEditorActiveBuffer: (editorId: string) => Readable<BufferInterface | null>
}

/**
 * Editor store interface
 */
export interface EditorStoreInterface {
    actions: EditorStoreActionsInterface
    getters: EditorStoreGettersInterface
}
