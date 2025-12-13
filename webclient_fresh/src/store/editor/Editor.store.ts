import { writable, derived } from 'svelte/store'
import { getContextClient } from '@urql/svelte'
import type {
    BufferInterface,
    TabInterface,
    EditorSettingsInterface,
    CreateBufferOptions,
    CreateTabOptions
} from '../../models/editor'
import type {
    EditorStateInterface,
    EditorStoreInterface,
    EditorStoreActionsInterface,
    EditorStoreGettersInterface
} from './models'
import { EXECUTE_CODE } from '../../api-client/graphql/queries'

// Helper function to generate unique IDs
function generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// Initial state
const initialState: EditorStateInterface = {
    buffers: new Map(),
    tabs: new Map(),
    activeTabId: null,
    settings: {
        theme: 'dark',
        fontSize: 14,
        fontFamily: 'Fira Code',
        tabSize: 4,
        showLineNumbers: true,
        lineWrapping: true,
        vimMode: false
    }
}

// Private writable store
const writableEditorStore = writable<EditorStateInterface>(initialState)

// Public hook
export function useEditorStore(): EditorStoreInterface {
    const client = getContextClient()

    // Actions: modify state
    const actions: EditorStoreActionsInterface = {
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

        createTab: (bufferId: string, title?: string): string => {
            const tabId = generateId()

            writableEditorStore.update(state => {
                const buffer = state.buffers.get(bufferId)
                if (!buffer) {
                    console.error(`Buffer ${bufferId} not found`)
                    return state
                }

                const tab: TabInterface = {
                    id: tabId,
                    bufferId,
                    title: title || buffer.name,
                    isActive: false,
                    isEditing: false,
                    isPinned: buffer.isStartupFile,
                    order: state.tabs.size
                }

                const newTabs = new Map(state.tabs)
                newTabs.set(tabId, tab)

                return {
                    ...state,
                    tabs: newTabs,
                    activeTabId: tabId
                }
            })

            return tabId
        },

        switchToTab: (tabId: string): void => {
            writableEditorStore.update(state => {
                if (!state.tabs.has(tabId)) {
                    console.error(`Tab ${tabId} not found`)
                    return state
                }

                // Update all tabs' isActive status
                const newTabs = new Map(state.tabs)
                newTabs.forEach((tab, id) => {
                    newTabs.set(id, { ...tab, isActive: id === tabId })
                })

                return {
                    ...state,
                    tabs: newTabs,
                    activeTabId: tabId
                }
            })
        },

        closeTab: (tabId: string): void => {
            writableEditorStore.update(state => {
                const tab = state.tabs.get(tabId)
                if (!tab) return state

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

                // Determine new active tab
                let newActiveTabId = state.activeTabId
                if (state.activeTabId === tabId) {
                    // Find startup tab first
                    for (const [id, t] of newTabs) {
                        const buf = newBuffers.get(t.bufferId)
                        if (buf?.isStartupFile) {
                            newActiveTabId = id
                            break
                        }
                    }
                    // If no startup tab, use first available
                    if (newActiveTabId === tabId && newTabs.size > 0) {
                        newActiveTabId = newTabs.keys().next().value || null
                    }
                }

                return {
                    ...state,
                    tabs: newTabs,
                    buffers: newBuffers,
                    activeTabId: newActiveTabId
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

        updateSettings: (settings: Partial<EditorSettingsInterface>): void => {
            writableEditorStore.update(state => ({
                ...state,
                settings: { ...state.settings, ...settings }
            }))
        },

        executeCode: async (code: string): Promise<{ success: boolean; message: string }> => {
            try {
                const result = await client.mutation(EXECUTE_CODE, { code })

                if (result.error) {
                    return {
                        success: false,
                        message: result.error.message
                    }
                }

                return {
                    success: result.data?.executeCode?.success || false,
                    message: result.data?.executeCode?.message || 'Unknown error'
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
    const activeTab = derived(writableEditorStore, $state =>
        $state.activeTabId ? $state.tabs.get($state.activeTabId) || null : null
    )

    const activeBuffer = derived(writableEditorStore, $state => {
        if (!$state.activeTabId) return null
        const tab = $state.tabs.get($state.activeTabId)
        if (!tab) return null
        return $state.buffers.get(tab.bufferId) || null
    })

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

    const getters: EditorStoreGettersInterface = {
        activeTab,
        activeBuffer,
        tabs,
        buffers,
        settings,
        startupBuffer
    }

    return { actions, getters }
}
