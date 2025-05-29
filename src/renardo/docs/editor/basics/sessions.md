# Sessions

Sessions in Renardo allow you to save and load your work, including all your code buffers and the associated startup file. This is essential for preserving your compositions and continuing your work across different sessions.

## Session Basics

A session in Renardo includes:

- All your open code buffers
- The selected startup file
- The state of your workspace

## Saving Sessions

To save your current work as a session:

1. Click the "Save Session" button in the toolbar or use the File menu
2. Enter a name for your session in the dialog that appears
3. Click "Save" to store your session

### What Gets Saved

When you save a session, Renardo will:

- Save the content of all your open tabs
- Record which startup file is associated with the session
- Store the session file in your Renardo user directory

## Loading Sessions

To load a previously saved session:

1. Open the right panel and select the "Sessions" tab
2. Browse the list of available session files
3. Click on a session name to load it

When you load a session, Renardo will:

- Open all the code buffers that were part of the session
- Restore the associated startup file
- Set the session name as the current session

## Managing Sessions

### Session Files Location

Session files are stored in your Renardo user directory:

- You can open this folder by clicking the "Open Sessions Folder" button in the Sessions panel
- Session files have a `.py` extension but contain special formatting to separate buffers

### Deleting Sessions

To delete a session:

1. Open your sessions folder using the "Open Sessions Folder" button
2. Delete the session file using your operating system's file manager
3. Refresh the sessions list in Renardo

## Session Structure

A session file is structured as follows:

- A header section containing metadata and the startup file
- Multiple sections for each code buffer, separated by delimiter lines
- Each section contains the buffer name and its content

## Tips for Effective Session Management

1. **Use descriptive names** - Name your sessions clearly to easily identify them later
2. **Create sessions for different projects** - Keep separate sessions for different musical projects
3. **Save regularly** - Save your session frequently to avoid losing work
4. **Create template sessions** - Save common starting points as template sessions
5. **Organize your sessions folder** - Delete or archive old sessions to keep the list manageable