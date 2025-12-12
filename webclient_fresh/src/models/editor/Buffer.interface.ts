/**
 * Buffer interface representing a text buffer in the editor
 */
export interface BufferInterface {
    id: string
    name: string
    content: string
    language: 'python' | 'javascript' | 'text' | 'sclang'
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
    language?: 'python' | 'javascript' | 'text' | 'sclang'
    isStartupFile?: boolean
    filePath?: string
    content?: string
}