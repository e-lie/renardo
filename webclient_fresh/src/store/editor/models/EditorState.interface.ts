import type { BufferInterface, TabInterface, EditorSettingsInterface } from '../../../models/editor'

/**
 * Editor state interface
 */
export interface EditorStateInterface {
    buffers: Map<string, BufferInterface>
    tabs: Map<string, TabInterface>
    activeTabId: string | null
    settings: EditorSettingsInterface
}
