import type { Readable } from 'svelte/store'
import type { Project, FileInfo } from '../../../models/project'

/**
 * Project store actions interface
 */
export interface ProjectStoreActionsInterface {
    openProject: (rootPath: string) => Promise<void>
    closeProject: () => void
    listFiles: (pattern?: string, recursive?: boolean) => Promise<FileInfo[]>
    readFile: (filePath: string) => Promise<string>
    writeFile: (filePath: string, content: string) => Promise<void>
}

/**
 * Project store getters interface
 */
export interface ProjectStoreGettersInterface {
    currentProject: Readable<Project | null>
    files: Readable<FileInfo[]>
}

/**
 * Project store interface
 */
export interface ProjectStoreInterface {
    actions: ProjectStoreActionsInterface
    getters: ProjectStoreGettersInterface
}
