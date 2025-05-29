# Code Execution

Renardo allows you to execute code in various ways, making it flexible for both step-by-step experimentation and running larger blocks of code.

## Execution Modes

There are three main ways to execute code in Renardo:

### 1. Single Line Execution (Mode 1)

Execute only the current line where the cursor is positioned.

- **Shortcut**: `Alt+Enter` (Windows/Linux) or `Option+Enter` (Mac)
- **When to use**: For executing commands one at a time, especially useful when building patterns incrementally

### 2. Paragraph or Selection Execution (Mode 2)

Execute the current paragraph (block of text without blank lines) or the currently selected text.

- **Shortcut**: `Ctrl+Enter` (Windows/Linux) or `Cmd+Enter` (Mac)
- **When to use**: For executing related commands together, such as setting up multiple instruments simultaneously

### 3. Stop All Sound (Emergency Stop)

Immediately stops all sound generation.

- **Shortcut**: `Ctrl+.` (Windows/Linux) or `Cmd+.` (Mac)
- **When to use**: When you need to silence everything quickly (equivalent to `Clock.clear()`)

## Execution Feedback

When code is executed:

1. The executed code is briefly highlighted to confirm what was run
2. Results, output, or errors appear in the console below the editor
3. Any sound or visual output is generated based on the code

## Execution State

Code execution in Renardo is:

- **Asynchronous** - Your interface remains responsive while code executes
- **Server-based** - Code is sent to the Renardo server for execution
- **Stateful** - Variables and objects persist between executions, allowing you to build on previous code

## Tips for Effective Code Execution

- Use Mode 1 (single line) for trying small changes or incremental building
- Use Mode 2 (paragraph) for related blocks of code that should run together
- Keep the emergency stop shortcut in mind for when things get too loud
- Watch the console for feedback on your code execution
- Remember that variables persist throughout your session unless explicitly cleared