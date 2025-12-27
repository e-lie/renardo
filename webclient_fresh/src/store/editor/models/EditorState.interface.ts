import type { BufferInterface, TabInterface, EditorSettingsInterface, EditorInstance } from '../../../models/editor'

/**
 * Editor state interface
 */
export interface EditorStateInterface {
    editors: Map<string, EditorInstance>  // Map of all editor instances
    buffers: Map<string, BufferInterface>
    tabs: Map<string, TabInterface>
    settings: EditorSettingsInterface
}
