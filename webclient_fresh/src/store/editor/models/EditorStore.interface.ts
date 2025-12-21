import type { Readable } from 'svelte/store'
import type { BufferInterface, TabInterface, EditorSettingsInterface, CreateBufferOptions, CreateTabOptions } from '../../../models/editor'

/**
 * Editor store actions interface
 */
export interface EditorStoreActionsInterface {
    createBuffer: (options: CreateBufferOptions) => string
    createTab: (bufferId: string, title?: string) => string
    switchToTab: (tabId: string) => void
    closeTab: (tabId: string) => void
    updateBufferContent: (bufferId: string, content: string) => void
    saveBuffer: (bufferId: string, filePath: string) => Promise<{ success: boolean; message: string }>
    renameBuffer: (bufferId: string, newName: string) => void
    updateTabTitle: (tabId: string, newTitle: string) => void
    updateSettings: (settings: Partial<EditorSettingsInterface>) => void
    executeCode: (code: string) => Promise<{ success: boolean; message: string }>
}

/**
 * Editor store getters interface
 */
export interface EditorStoreGettersInterface {
    activeTab: Readable<TabInterface | null>
    activeBuffer: Readable<BufferInterface | null>
    tabs: Readable<TabInterface[]>
    buffers: Readable<BufferInterface[]>
    settings: Readable<EditorSettingsInterface>
    startupBuffer: Readable<BufferInterface | null>
}

/**
 * Editor store interface
 */
export interface EditorStoreInterface {
    actions: EditorStoreActionsInterface
    getters: EditorStoreGettersInterface
}
