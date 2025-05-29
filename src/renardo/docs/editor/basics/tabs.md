# Working with Tabs

The Renardo editor supports multiple tabs to help you organize your code into separate buffers. This allows you to work on different parts of your project simultaneously.

## Tab Types

There are two main types of tabs in the Renardo editor:

1. **Startup File Tabs** - Special tabs that contain code executed when Renardo starts. These tabs are always the first tab.
2. **Regular Code Tabs** - Standard tabs for your live coding work.

## Tab Management

### Creating New Tabs

To create a new tab:

1. Click the "+" button in the tab bar
2. Enter a name for your new buffer
3. Click "Create" or press Enter

### Switching Between Tabs

To switch to a different tab, simply click on its tab in the tab bar. The editor will display the content of the selected tab.

### Renaming Tabs

To rename a tab:

1. Double-click on the tab name
2. Enter the new name
3. Press Enter or click elsewhere to confirm

### Closing Tabs

To close a tab:

1. Click the "x" button on the tab
2. Confirm the closure if prompted (especially if there are unsaved changes)

Note that you cannot close the last remaining tab.

## Special Tab Behavior

### Startup Files

Startup file tabs have special behavior:

- They are always displayed first in the tab list
- They have a distinct visual indicator
- When saved, they are stored in your Renardo startup files location
- They can be selected as the default startup file for Renardo

## Tab Content Persistence

The content of your tabs persists in the following ways:

- During your session: All tab content is maintained in browser memory
- When saving a session: All tab content is saved in the session file
- Startup files: These are saved to disk when explicitly saved

## Keyboard Navigation

You can navigate between tabs using keyboard shortcuts:

- `Ctrl+Tab` (Windows/Linux) or `Cmd+Tab` (Mac): Switch to the next tab
- `Ctrl+Shift+Tab` (Windows/Linux) or `Cmd+Shift+Tab` (Mac): Switch to the previous tab

## Best Practices

- Use descriptive names for your tabs to easily identify their purpose
- Consider using one tab per musical concept or pattern
- Keep your startup file separate from your live coding sessions
- Close unused tabs to reduce clutter
- Use sessions to save the state of all your tabs