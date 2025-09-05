# Integration Guide: New Tab/Buffer Architecture

## Overview

The new architecture separates **TextBuffers** (content units) from **EditorTabs** (UI frames). This provides:

- **Clean separation**: UI (tabs) vs content (buffers)
- **Buffer-based sessions**: Sessions save/load based on buffers, not UI state
- **Progressive TypeScript**: Core classes in TypeScript, JS wrapper for easy integration
- **Buffer-centric naming**: Tab titles always reflect buffer names

## Key Classes

### TextBuffer (TypeScript)
- Manages code content, metadata, history
- Independent of UI representation
- Has undo/redo, dirty tracking, readonly support

### EditorTab (TypeScript)
- UI frame that displays a TextBuffer
- Multiple tabs can show the same buffer (future: split view)
- Tab title always matches buffer name

### TabManager (TypeScript)
- Coordinates tabs and buffers
- Handles creation, switching, removal
- Session export/import with concatenated format

## Integration Examples

### Replace old tab management in CodeEditor.svelte:

```javascript
// Instead of old direct tab manipulation:
// tabs = [...tabs, newTab];
// activeTabId = newTab.id;

// Use the new system:
import { 
  tabManager, 
  createNewTab, 
  switchToTab, 
  loadContentInTab,
  updateCurrentTabContent,
  saveSessionToServer
} from '$lib/editor/editorStore.js';

// Reactive stores
$: tabs = $tabManager.tabs;
$: activeTab = $tabManager.activeTab;
$: activeBuffer = $tabManager.activeBuffer;
$: startupBuffer = $tabManager.startupBuffer;

// Event handlers
function handleNewTab() {
  createNewTab('Untitled', '', 'manual');
}

function handleSwitchTab(event) {
  switchToTab(event.detail.tabId);
}

function handleLoadTutorial(file) {
  const name = file.name.replace('.py', '');
  loadContentInTab(name, file.content, 'tutorial');
}

function handleEditorChange(event) {
  updateCurrentTabContent(event.detail.value);
}

function handleSaveSession(sessionName) {
  return saveSessionToServer(sessionName);
}
```

### Update EditorTabs.svelte component:

```javascript
// The tabs prop now contains EditorTab instances
// Get display data like this:
$: tabData = tabs.map(tab => {
  const tabState = tab.getState();
  const buffer = $tabManager.buffers?.get(tabState.bufferId);
  const bufferMeta = buffer?.getMetadata();
  
  return {
    id: tabState.id,
    name: tabState.title, // This comes from buffer name
    isEditing: tabState.isEditing,
    isPinned: tabState.isPinned,
    isStartup: bufferMeta?.isStartupFile || false,
    dirty: buffer ? get(buffer.dirty) : false
  };
});
```

## Session Format

The new system maintains the same concatenated session format:

```
//==============================================================================
// STARTUP_FILE: startup.py
//==============================================================================
# Startup content here

################################################################################
######## Buffer1Name
################################################################################
# Buffer 1 content here
################################################################################
######## Buffer2Name
################################################################################
# Buffer 2 content here
```

But now sessions are based on **buffers**, not tabs:
- Each buffer appears once in the session
- Buffer names determine section headers
- Startup buffer is always included if it exists

## Migration Strategy

1. **Start with session management**: Replace `doSaveSession()` and session loading
2. **Update tab creation**: Replace `createNewBuffer()` with `createNewTab()`
3. **Update tab switching**: Replace `handleSwitchTab()` logic
4. **Update content loading**: Replace tutorial/example loading functions
5. **Update tab renaming**: Use buffer renaming instead of tab renaming
6. **Test thoroughly**: Ensure all existing functionality works

## Benefits

- **Cleaner code**: Separation of concerns
- **Type safety**: Progressive TypeScript adoption
- **Better architecture**: Tabs are just UI, buffers hold content
- **Future ready**: Easy to add split views, buffer management
- **Consistent naming**: Tab names always match buffer names
- **Same session format**: No breaking changes to saved sessions