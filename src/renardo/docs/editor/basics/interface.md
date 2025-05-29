# Interface Overview

The Renardo Editor interface is designed to provide an efficient environment for live coding. This page explains the main components of the editor interface.

## Layout

The editor is divided into several main sections:

![Editor Layout](../../images/editor-layout.png)

1. **Tab Bar** - Navigate between open code buffers
2. **Code Editor** - The main area where you write code
3. **Console** - Displays output and messages from code execution
4. **Right Panel** - Contains tutorials, sessions, and startup files
5. **Status Bar** - Shows current state and provides access to common actions

## Code Editor

The main editor area uses CodeMirror with Python syntax highlighting and various helpful features:

- Line numbers for easy reference
- Syntax highlighting for better readability
- Automatic bracket matching and closing
- Execution highlighting to show which code is running

## Console

The console panel displays:

- Messages from the Renardo runtime
- Execution results and feedback
- Error messages and warnings
- System status notifications

You can resize the console by dragging the divider between the editor and console, or minimize it to give more space to the editor.

## Right Panel

The right panel contains multiple tabs:

- **Tutorial** - Browse and load tutorial files
- **Sessions** - Save and load session files
- **Startup Files** - Manage files that run when Renardo starts
- **Documentation** - Access this documentation

The panel can be resized by dragging its left edge, or hidden completely using the toggle button.

## Zen Mode

For distraction-free coding, you can toggle Zen Mode, which hides all panels and UI elements except the code editor and a minimal console. This is perfect for performances or focused coding sessions.

## Responsive Design

The editor interface is fully responsive and will adapt to different screen sizes and orientations. All panels can be resized or hidden to customize your workspace according to your needs.