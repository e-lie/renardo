export interface EditorInstance {
  id: string              // Unique editor ID (generated on registration)
  componentId: string     // Component ID for identification
  tabIds: string[]        // List of tab IDs belonging to this editor
  activeTabId: string | null  // Currently active tab in this editor
  createdAt: Date         // Timestamp when editor was registered
}
