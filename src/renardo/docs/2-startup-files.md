# Startup Files

Startup files in Renardo contain code that runs automatically when the environment initializes. They allow you to set up your default environment, define custom functions, and prepare your workspace.

## What are Startup Files?

Startup files are special Python files that:

- Run automatically when Renardo starts
- Set up your default musical environment
- Define commonly used variables and functions
- Configure system parameters
- Import additional libraries or extensions

## Accessing Startup Files

To access and manage startup files:

1. Open the right panel if it's not already visible
2. Select the "Startup Files" tab
3. Browse the list of available startup files

## Creating a New Startup File

To create a new startup file:

1. In the Startup Files panel, click "New Startup File"
2. Enter a name for your file (e.g., "my_setup.py")
3. A new startup file will be created and opened in the editor
4. Add your initialization code
5. Save the file

## Editing Startup Files

Startup files appear as special tabs in the editor:

- They are always the first tab when open
- They have a distinct visual indicator
- Changes to startup files must be explicitly saved

To edit a startup file:

1. Select it from the Startup Files panel
2. Make your changes in the editor
3. Click "Save Startup File" to store your changes

## Setting a Default Startup File

You can designate one startup file as the default, which will be loaded automatically when Renardo starts:

1. In the Startup Files panel, find the file you want to make default
2. Click the "Set as Default" button next to that file
3. The file will be marked as the default startup file

## Startup File Content Examples

Typical startup file content includes:

```python
# Set up default root note and scale
Root.default = 0
Scale.default = Scale.minor

# Define commonly used rhythm patterns
d_pat = P[1,0,0,1,0,1,0,0]
s_pat = P[0,0,1,0,0,0,1,0]

# Configure audio parameters
Clock.bpm = 120
```

## Managing Startup Files

To manage your startup files:

- **Open Folder**: Click "Open Startup Files Folder" to browse the files in your file manager
- **Rename**: Use your operating system's file manager to rename files
- **Delete**: Use your operating system's file manager to delete unwanted files
- **Organize**: Create a system for naming your startup files based on their purpose

## Best Practices

1. **Keep it modular** - Create different startup files for different projects or styles
2. **Comment thoroughly** - Document what your startup code does
3. **Test before saving** - Make sure your startup code runs without errors
4. **Don't overload** - Only include essential setup code to keep startup times fast
5. **Version control** - Consider backing up important startup files