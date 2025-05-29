# Code Execution Shortcuts

These shortcuts control how code is executed in the Renardo editor.

## Primary Execution Shortcuts

| Action | Windows/Linux | Mac | Description |
|--------|--------------|-----|-------------|
| Execute Current Line | Alt+Enter | Option+Enter | Executes only the line where the cursor is currently positioned |
| Execute Paragraph/Selection | Ctrl+Enter | Cmd+Enter | Executes the current paragraph (block without blank lines) or the selected text |
| Stop All Sound | Ctrl+. | Cmd+. | Immediately stops all sound generation (equivalent to `Clock.clear()`) |

## When to Use Each Mode

- **Single Line Execution (Mode 1)** - Perfect for incremental building, testing small changes, or advancing step by step through a sequence
- **Paragraph Execution (Mode 2)** - Ideal for running related blocks of code together, such as setting up multiple instruments or defining several variables
- **Stop All Sound** - Essential for silencing runaway patterns or when you need to start fresh

## Advanced Execution Techniques

### Using Selection with Mode 2

You can precisely control which code executes by selecting specific lines before pressing Ctrl+Enter (Cmd+Enter on Mac):

1. Click and drag to select multiple lines of code
2. Use Shift+Arrow keys to extend selection
3. Press Ctrl+Enter (Cmd+Enter) to execute only the selected code

### Executing the Entire Buffer

To execute all code in the current buffer:

1. Select all text (Ctrl+A or Cmd+A)
2. Press Ctrl+Enter (Cmd+Enter)

### Handling Long-Running Code

If code execution seems to hang or produces unexpected audio:

1. Press Ctrl+. (Cmd+.) to stop all sound
2. Check the console for error messages
3. Modify your code to fix any issues
4. Try executing smaller sections to isolate problems