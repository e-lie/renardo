/**
 * Buffer interface representing a text buffer in the editor
 */
export type BufferLanguage = 'python' | 'hydra'

export interface BufferInterface {
    id: string
    name: string
    content: string
    language: BufferLanguage
    isStartupFile: boolean
    isDirty: boolean
    filePath?: string
    createdAt: Date
    updatedAt: Date
}

/**
 * Options for creating a new buffer
 */
export interface CreateBufferOptions {
    name: string
    language?: BufferLanguage
    isStartupFile?: boolean
    filePath?: string
    content?: string
}