import { writable, derived } from 'svelte/store'
import type { Project, FileInfo } from '../../models/project'
import type {
    ProjectStoreInterface,
    ProjectStoreActionsInterface,
    ProjectStoreGettersInterface
} from './models'

interface ProjectState {
    currentProject: Project | null
    files: FileInfo[]
}

const initialState: ProjectState = {
    currentProject: null,
    files: []
}

const writableProjectStore = writable<ProjectState>(initialState)

export function useProjectStore(): ProjectStoreInterface {
    const actions: ProjectStoreActionsInterface = {
        openProject: async (rootPath: string): Promise<void> => {
            try {
                const response = await fetch('http://localhost:8000/api/project/open', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ root_path: rootPath })
                })

                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData.detail || 'Failed to open project')
                }

                const data = await response.json()
                writableProjectStore.update(state => ({
                    ...state,
                    currentProject: data.project
                }))
            } catch (error) {
                console.error('Error opening project:', error)
                throw error
            }
        },

        closeProject: (): void => {
            writableProjectStore.set(initialState)
        },

        listFiles: async (pattern: string = '*', recursive: boolean = false): Promise<FileInfo[]> => {
            // TODO: Call API to list files
            const files: FileInfo[] = []
            writableProjectStore.update(state => ({
                ...state,
                files
            }))
            return files
        },

        readFile: async (filePath: string): Promise<string> => {
            // TODO: Call API to read file
            return ''
        },

        writeFile: async (filePath: string, content: string): Promise<void> => {
            try {
                const response = await fetch('http://localhost:8000/api/project/save-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ file_path: filePath, content })
                })

                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData.detail || 'Failed to save file')
                }
            } catch (error) {
                console.error('Error saving file:', error)
                throw error
            }
        }
    }

    const currentProject = derived(writableProjectStore, $state => $state.currentProject)
    const files = derived(writableProjectStore, $state => $state.files)

    const getters: ProjectStoreGettersInterface = {
        currentProject,
        files
    }

    return { actions, getters }
}
