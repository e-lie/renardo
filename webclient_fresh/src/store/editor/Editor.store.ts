import { writable, derived } from 'svelte/store'
import type {
    BufferInterface,
    TabInterface,
    EditorSettingsInterface,
    EditorInstance,
    CreateBufferOptions,
    CreateTabOptions
} from '../../models/editor'
import type {
    EditorStateInterface,
    EditorStoreInterface,
    EditorStoreActionsInterface,
    EditorStoreGettersInterface
} from './models'
import { executeCode as executeCodeApi } from '../../api-client/rest/api'

// Helper function to generate unique IDs
function generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// Load settings from localStorage
function loadSettingsFromLocalStorage(): EditorSettingsInterface {
    const savedSettings = localStorage.getItem('editor-settings')
    if (savedSettings) {
        try {
            return JSON.parse(savedSettings)
        } catch (e) {
            console.error('Failed to parse editor settings from localStorage:', e)
        }
    }
    return {
        theme: 'dracula',
        fontSize: 14,
        fontFamily: 'Fira Code',
        tabSize: 4,
        showLineNumbers: true,
        lineWrapping: true,
        vimMode: false
    }
}

// Initial state
const initialState: EditorStateInterface = {
    editors: new Map(),
    buffers: new Map(),
    tabs: new Map(),
    settings: loadSettingsFromLocalStorage()
}

// Private writable store
const writableEditorStore = writable<EditorStateInterface>(initialState)

// Public hook
export function useEditorStore(): EditorStoreInterface {
    // Actions: modify state
    const actions: EditorStoreActionsInterface = {
        registerEditor: (componentId: string): string => {
            const editorId = generateId()

            const editorInstance: EditorInstance = {
                id: editorId,
                componentId,
                tabIds: [],
                activeTabId: null,
                createdAt: new Date()
            }

            writableEditorStore.update(state => {
                const newEditors = new Map(state.editors)
                newEditors.set(editorId, editorInstance)
                return { ...state, editors: newEditors }
            })

            return editorId
        },

        unregisterEditor: (editorId: string): void => {
            writableEditorStore.update(state => {
                const editor = state.editors.get(editorId)
                if (!editor) {
                    console.error(`Editor ${editorId} not found`)
                    return state
                }

                // Remove all tabs belonging to this editor
                const newTabs = new Map(state.tabs)
                editor.tabIds.forEach(tabId => {
                    newTabs.delete(tabId)
                })

                // Collect buffers used by this editor's tabs
                const buffersUsedByEditor = new Set<string>()
                editor.tabIds.forEach(tabId => {
                    const tab = state.tabs.get(tabId)
                    if (tab) {
                        buffersUsedByEditor.add(tab.bufferId)
                    }
                })

                // Check if buffers are still used by other editors' tabs
                const newBuffers = new Map(state.buffers)
                buffersUsedByEditor.forEach(bufferId => {
                    let bufferStillUsed = false
                    for (const [tabId, tab] of newTabs) {
                        if (tab.bufferId === bufferId) {
                            bufferStillUsed = true
                            break
                        }
                    }
                    if (!bufferStillUsed) {
                        newBuffers.delete(bufferId)
                    }
                })

                // Remove editor
                const newEditors = new Map(state.editors)
                newEditors.delete(editorId)

                return {
                    ...state,
                    editors: newEditors,
                    tabs: newTabs,
                    buffers: newBuffers
                }
            })
        },

        createBuffer: (options: CreateBufferOptions): string => {
            const bufferId = generateId()
            const now = new Date()

            const buffer: BufferInterface = {
                id: bufferId,
                name: options.name,
                content: options.content || '',
                language: 'python', // Force Python for all buffers
                isStartupFile: options.isStartupFile || false,
                isDirty: false,
                filePath: options.filePath,
                createdAt: now,
                updatedAt: now
            }

            writableEditorStore.update(state => {
                const newBuffers = new Map(state.buffers)
                newBuffers.set(bufferId, buffer)
                return { ...state, buffers: newBuffers }
            })

            return bufferId
        },

        createTab: (editorId: string, bufferId: string, title?: string): string => {
            const tabId = generateId()

            writableEditorStore.update(state => {
                const editor = state.editors.get(editorId)
                if (!editor) {
                    console.error(`Editor ${editorId} not found`)
                    return state
                }

                const buffer = state.buffers.get(bufferId)
                if (!buffer) {
                    console.error(`Buffer ${bufferId} not found`)
                    return state
                }

                const tab: TabInterface = {
                    id: tabId,
                    bufferId,
                    editorId,
                    title: title || buffer.name,
                    isActive: false,
                    isEditing: false,
                    isPinned: buffer.isStartupFile,
                    order: state.tabs.size
                }

                const newTabs = new Map(state.tabs)
                newTabs.set(tabId, tab)

                const updatedEditor: EditorInstance = {
                    ...editor,
                    tabIds: [...editor.tabIds, tabId],
                    activeTabId: tabId
                }

                const newEditors = new Map(state.editors)
                newEditors.set(editorId, updatedEditor)

                return {
                    ...state,
                    editors: newEditors,
                    tabs: newTabs
                }
            })

            return tabId
        },

        loadContentInNewTab: (editorId: string, content: string, title: string, filePath?: string): string => {
            let bufferId = ''
            let tabId = ''

            writableEditorStore.update(state => {
                const editor = state.editors.get(editorId)
                if (!editor) {
                    console.error(`Editor ${editorId} not found`)
                    return state
                }

                // Create buffer with content
                bufferId = generateId()
                const buffer: BufferInterface = {
                    id: bufferId,
                    name: title,
                    content,
                    language: 'python',
                    isDirty: false,
                    isStartupFile: false,
                    filePath,
                    createdAt: new Date(),
                    updatedAt: new Date()
                }

                // Create tab
                tabId = generateId()
                const tab: TabInterface = {
                    id: tabId,
                    bufferId,
                    editorId,
                    title,
                    isActive: true,
                    isEditing: false,
                    isPinned: false,
                    order: state.tabs.size
                }

                const newBuffers = new Map(state.buffers)
                newBuffers.set(bufferId, buffer)

                const newTabs = new Map(state.tabs)
                // Deactivate all other tabs OF THIS EDITOR ONLY
                editor.tabIds.forEach(existingTabId => {
                    const existingTab = state.tabs.get(existingTabId)
                    if (existingTab) {
                        newTabs.set(existingTabId, { ...existingTab, isActive: false })
                    }
                })
                newTabs.set(tabId, tab)

                const updatedEditor: EditorInstance = {
                    ...editor,
                    tabIds: [...editor.tabIds, tabId],
                    activeTabId: tabId
                }

                const newEditors = new Map(state.editors)
                newEditors.set(editorId, updatedEditor)

                return {
                    ...state,
                    editors: newEditors,
                    buffers: newBuffers,
                    tabs: newTabs
                }
            })

            return tabId
        },

        switchToTab: (editorId: string, tabId: string): void => {
            writableEditorStore.update(state => {
                const editor = state.editors.get(editorId)
                if (!editor) {
                    console.error(`Editor ${editorId} not found`)
                    return state
                }

                const tab = state.tabs.get(tabId)
                if (!tab) {
                    console.error(`Tab ${tabId} not found`)
                    return state
                }

                // Verify tab belongs to this editor
                if (tab.editorId !== editorId) {
                    console.error(`Tab ${tabId} does not belong to editor ${editorId}`)
                    return state
                }

                // Update all tabs' isActive status FOR THIS EDITOR ONLY
                const newTabs = new Map(state.tabs)
                editor.tabIds.forEach(tid => {
                    const t = state.tabs.get(tid)
                    if (t) {
                        newTabs.set(tid, { ...t, isActive: tid === tabId })
                    }
                })

                const updatedEditor: EditorInstance = {
                    ...editor,
                    activeTabId: tabId
                }

                const newEditors = new Map(state.editors)
                newEditors.set(editorId, updatedEditor)

                return {
                    ...state,
                    editors: newEditors,
                    tabs: newTabs
                }
            })
        },

        closeTab: (editorId: string, tabId: string): void => {
            writableEditorStore.update(state => {
                const editor = state.editors.get(editorId)
                if (!editor) {
                    console.error(`Editor ${editorId} not found`)
                    return state
                }

                const tab = state.tabs.get(tabId)
                if (!tab) return state

                // Verify tab belongs to this editor
                if (tab.editorId !== editorId) {
                    console.error(`Tab ${tabId} does not belong to editor ${editorId}`)
                    return state
                }

                const buffer = state.buffers.get(tab.bufferId)

                // Can't close startup file tab
                if (buffer?.isStartupFile) {
                    console.warn('Cannot close startup file tab')
                    return state
                }

                // Check if this is the last tab showing this buffer
                let bufferStillUsed = false
                for (const [otherTabId, otherTab] of state.tabs) {
                    if (otherTabId !== tabId && otherTab.bufferId === tab.bufferId) {
                        bufferStillUsed = true
                        break
                    }
                }

                // Remove tab
                const newTabs = new Map(state.tabs)
                newTabs.delete(tabId)

                // Remove buffer if no longer used
                const newBuffers = new Map(state.buffers)
                if (!bufferStillUsed) {
                    newBuffers.delete(tab.bufferId)
                }

                // Update editor: remove tabId from tabIds
                const updatedTabIds = editor.tabIds.filter(tid => tid !== tabId)

                // Determine new active tab for this editor
                let newActiveTabId = editor.activeTabId
                if (editor.activeTabId === tabId) {
                    // Find startup tab first (among this editor's tabs)
                    for (const tid of updatedTabIds) {
                        const t = newTabs.get(tid)
                        if (t) {
                            const buf = newBuffers.get(t.bufferId)
                            if (buf?.isStartupFile) {
                                newActiveTabId = tid
                                break
                            }
                        }
                    }
                    // If no startup tab, use first available tab of this editor
                    if (newActiveTabId === tabId && updatedTabIds.length > 0) {
                        newActiveTabId = updatedTabIds[0] || null
                    } else if (updatedTabIds.length === 0) {
                        newActiveTabId = null
                    }
                }

                const updatedEditor: EditorInstance = {
                    ...editor,
                    tabIds: updatedTabIds,
                    activeTabId: newActiveTabId
                }

                const newEditors = new Map(state.editors)
                newEditors.set(editorId, updatedEditor)

                return {
                    ...state,
                    editors: newEditors,
                    tabs: newTabs,
                    buffers: newBuffers
                }
            })
        },

        updateBufferContent: (bufferId: string, content: string): void => {
            writableEditorStore.update(state => {
                const buffer = state.buffers.get(bufferId)
                if (!buffer) return state

                const updatedBuffer: BufferInterface = {
                    ...buffer,
                    content,
                    isDirty: true,
                    updatedAt: new Date()
                }

                const newBuffers = new Map(state.buffers)
                newBuffers.set(bufferId, updatedBuffer)

                return { ...state, buffers: newBuffers }
            })
        },

        renameBuffer: (bufferId: string, newName: string): void => {
            writableEditorStore.update(state => {
                const buffer = state.buffers.get(bufferId)
                if (!buffer) return state

                const updatedBuffer: BufferInterface = {
                    ...buffer,
                    name: newName,
                    updatedAt: new Date()
                }

                const newBuffers = new Map(state.buffers)
                newBuffers.set(bufferId, updatedBuffer)

                // Update all tabs displaying this buffer
                const newTabs = new Map(state.tabs)
                newTabs.forEach((tab, id) => {
                    if (tab.bufferId === bufferId) {
                        newTabs.set(id, { ...tab, title: newName })
                    }
                })

                return { ...state, buffers: newBuffers, tabs: newTabs }
            })
        },

        saveBuffer: async (bufferId: string, filePath: string): Promise<{ success: boolean; message: string }> => {
            return new Promise((resolve) => {
                writableEditorStore.update(state => {
                    const buffer = state.buffers.get(bufferId)

                    if (!buffer) {
                        resolve({
                            success: false,
                            message: 'Buffer not found'
                        })
                        return state
                    }

                    // Call API to save file to project
                    fetch('http://localhost:8000/api/project/save-file', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ file_path: filePath, content: buffer.content })
                    })
                        .then(async response => {
                            if (!response.ok) {
                                const errorData = await response.json()
                                throw new Error(errorData.detail || 'Failed to save file')
                            }
                            return response.json()
                        })
                        .then(() => {
                            writableEditorStore.update(state => {
                                // Extract filename from path
                                const fileName = filePath.split('/').pop() || filePath

                                const updatedBuffer = {
                                    ...buffer,
                                    name: fileName.replace('.py', ''),
                                    filePath,
                                    isDirty: false,
                                    updatedAt: new Date()
                                }

                                const newBuffers = new Map(state.buffers)
                                newBuffers.set(bufferId, updatedBuffer)

                                // Update all tabs displaying this buffer
                                const newTabs = new Map(state.tabs)
                                newTabs.forEach((tab, id) => {
                                    if (tab.bufferId === bufferId) {
                                        newTabs.set(id, { ...tab, title: fileName.replace('.py', '') })
                                    }
                                })

                                return { ...state, buffers: newBuffers, tabs: newTabs }
                            })

                            resolve({
                                success: true,
                                message: `File saved: ${filePath}`
                            })
                        })
                        .catch(error => {
                            resolve({
                                success: false,
                                message: error instanceof Error ? error.message : 'Failed to save file'
                            })
                        })

                    return state
                })
            })
        },

        updateTabTitle: (tabId: string, newTitle: string): void => {
            writableEditorStore.update(state => {
                const tab = state.tabs.get(tabId)
                if (!tab) return state

                const newTabs = new Map(state.tabs)
                newTabs.set(tabId, { ...tab, title: newTitle })

                return { ...state, tabs: newTabs }
            })
        },

        updateSettings: (settings: Partial<EditorSettingsInterface>): void => {
            writableEditorStore.update(state => {
                const newSettings = { ...state.settings, ...settings }
                // Save to localStorage
                localStorage.setItem('editor-settings', JSON.stringify(newSettings))
                return {
                    ...state,
                    settings: newSettings
                }
            })
        },

        executeCode: async (code: string): Promise<{ success: boolean; message: string }> => {
            try {
                const result = await executeCodeApi(code)

                return {
                    success: result.success,
                    message: result.message
                }
            } catch (error) {
                return {
                    success: false,
                    message: error instanceof Error ? error.message : 'Unknown error'
                }
            }
        }
    }

    // Getters: read-only derived stores
    const tabs = derived(writableEditorStore, $state =>
        Array.from($state.tabs.values()).sort((a, b) => a.order - b.order)
    )

    const buffers = derived(writableEditorStore, $state =>
        Array.from($state.buffers.values())
    )

    const settings = derived(writableEditorStore, $state => $state.settings)

    const startupBuffer = derived(writableEditorStore, $state => {
        for (const buffer of $state.buffers.values()) {
            if (buffer.isStartupFile) {
                return buffer
            }
        }
        return null
    })

    // Editor-specific getter functions
    const getEditor = (editorId: string) => {
        return derived(writableEditorStore, $state =>
            $state.editors.get(editorId) || null
        )
    }

    const getEditorTabs = (editorId: string) => {
        return derived(writableEditorStore, $state => {
            const editor = $state.editors.get(editorId)
            if (!editor) return []

            return editor.tabIds
                .map(tabId => $state.tabs.get(tabId))
                .filter((tab): tab is TabInterface => tab !== undefined)
                .sort((a, b) => a.order - b.order)
        })
    }

    const getEditorActiveTab = (editorId: string) => {
        return derived(writableEditorStore, $state => {
            const editor = $state.editors.get(editorId)
            if (!editor || !editor.activeTabId) return null
            return $state.tabs.get(editor.activeTabId) || null
        })
    }

    const getEditorActiveBuffer = (editorId: string) => {
        return derived(writableEditorStore, $state => {
            const editor = $state.editors.get(editorId)
            if (!editor || !editor.activeTabId) return null

            const tab = $state.tabs.get(editor.activeTabId)
            if (!tab) return null

            return $state.buffers.get(tab.bufferId) || null
        })
    }

    const getters: EditorStoreGettersInterface = {
        tabs,
        buffers,
        settings,
        startupBuffer,
        getEditor,
        getEditorTabs,
        getEditorActiveTab,
        getEditorActiveBuffer
    }

    return { actions, getters }
}
