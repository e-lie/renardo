/**
 * Tab interface representing a tab in the editor
 */
export interface TabInterface {
    id: string
    bufferId: string
    editorId: string  // ID of the editor this tab belongs to
    title: string
    isActive: boolean
    isEditing: boolean
    isPinned: boolean
    order: number
}

/**
 * Options for creating a new tab
 */
export interface CreateTabOptions {
    bufferId: string
    title?: string
    order?: number
}
