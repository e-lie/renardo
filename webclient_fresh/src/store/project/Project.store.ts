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
            // TODO: Call API to open project
            writableProjectStore.update(state => ({
                ...state,
                currentProject: { root_path: rootPath }
            }))
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
            // TODO: Call API to write file
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
