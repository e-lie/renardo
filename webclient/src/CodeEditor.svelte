<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade } from 'svelte/transition';
  import { appState, initWebSocket, sendMessage } from './lib/websocket.js';
  // We'll load CodeMirror and its dependencies from CDN
  
  // State for editor content
  let editorContent = `# Renardo Live Coding Editor
# Type your code here and press Ctrl+Enter to run

d1 >> play("x-o-").every(4, "stutter", 4)
d2 >> blip([_,_,4,_], dur=.5)
`;

  // CodeMirror options
  const editorOptions = {
    lineNumbers: true,
    theme: 'default',
    tabSize: 4,
    indentWithTabs: false,
    autoCloseBrackets: true,
    matchBrackets: true,
    highlightSelectionMatches: true,
  };
  
  // Runtime status
  let scBackendRunning = false;
  let renardoRuntimeRunning = false;
  
  // Editor container reference
  let editorContainer;
  let editor;
  
  // Console output
  let consoleOutput = [];
  let consoleContainer;
  
  // We'll assume websockets are managed by the parent App component
  
  // Function to scroll console to bottom
  function scrollToBottom() {
    if (consoleContainer) {
      setTimeout(() => {
        consoleContainer.scrollTop = consoleContainer.scrollHeight;
      }, 50);
    }
  }
  
  // Initialize CodeMirror on mount
  onMount(() => {
    // Function to load a script dynamically
    const loadScript = (src) => {
      return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = () => resolve();
        script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
        document.head.appendChild(script);
      });
    };
    
    // Function to load a CSS file dynamically
    const loadCSS = (href) => {
      return new Promise((resolve, reject) => {
        // Check if the CSS is already loaded
        const existingLink = document.querySelector(`link[href="${href}"]`);
        if (existingLink) {
          resolve();
          return;
        }
        
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        link.onload = () => resolve();
        link.onerror = () => reject(new Error(`Failed to load CSS: ${href}`));
        document.head.appendChild(link);
      });
    };
    
    // Wait for CodeMirror to be loaded from CDN and load additional modes
    const initEditor = async () => {
      if (typeof window.CodeMirror === 'undefined') {
        // If CodeMirror isn't loaded yet, try again in 100ms
        setTimeout(initEditor, 100);
        return;
      }
      
      try {
        // Load CodeMirror core CSS
        await loadCSS('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/codemirror.min.css');
        
        // Load Monokai theme CSS
        await loadCSS('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/theme/monokai.min.css');
        
        // Load CodeMirror addons and modes for better editor experience
        await Promise.all([
          // Python mode for syntax highlighting
          loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/mode/python/python.min.js'),
          // Matching brackets highlighting
          loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/edit/matchbrackets.min.js'),
          // Auto-close brackets
          loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/edit/closebrackets.min.js'),
          // Highlight active line
          loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/selection/active-line.min.js'),
          // Search/replace functionality
          loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/search/search.min.js'),
          loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/search/searchcursor.min.js'),
          // Highlight selection matches
          loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/search/match-highlighter.min.js')
        ]).catch(err => {
          console.error("Error loading CodeMirror addons:", err);
        });
        
        // Initialize CodeMirror
        const codeMirrorOptions = {
          value: editorContent,
          lineNumbers: true,
          mode: {
            name: 'python',
            version: 3,
            singleLineStringErrors: false
          },
          theme: 'monokai',
          tabSize: 4,
          indentWithTabs: false,
          indentUnit: 4,
          lineWrapping: true,
          viewportMargin: Infinity,
          matchBrackets: true,
          autoCloseBrackets: true,
          styleActiveLine: true,
          smartIndent: true,
          electricChars: true,
          highlightSelectionMatches: true,
          autofocus: true
        };
      
        // Make sure we have the CodeMirror textarea element
        const textarea = document.getElementById('code-editor');
        if (textarea) {
          // Initialize CodeMirror
          editor = window.CodeMirror.fromTextArea(textarea, codeMirrorOptions);
          
          // Update local content when editor changes
          editor.on('change', (instance) => {
            editorContent = instance.getValue();
          });
          
          // Add key bindings for different execution modes
          editor.setOption('extraKeys', {
            'Ctrl-Enter': executeCode,       // Mode 2: Execute paragraph or selection
            'Cmd-Enter': executeCode,        // For Mac
            'Alt-Enter': executeCurrentLine, // Mode 1: Execute current line
            'Alt-Cmd-Enter': executeCurrentLine, // For Mac Alt+Enter
            'Ctrl-.': stopMusic,            // Stop all music
            'Cmd-.': stopMusic              // For Mac
          });
          
          // Log successful initialization
          console.log("CodeMirror editor initialized with Python syntax highlighting");
        } else {
          console.error("Could not find code-editor textarea element");
        }
      } catch (error) {
        console.error("Error initializing CodeMirror editor:", error);
      }
    };
    
    // Start the initialization process
    initEditor();
    
    // Subscribe to appState changes
    const unsubscribe = appState.subscribe(state => {
      if (state.consoleOutput && state.consoleOutput.length > 0) {
        const prevOutputCount = consoleOutput.length;
        consoleOutput = state.consoleOutput;
        
        // If new console output was added, scroll to bottom
        if (consoleOutput.length > prevOutputCount) {
          scrollToBottom();
        }
      }
    });
    
    // Set up keyboard shortcuts for execution - fallback for whole document
    const handleKeyDown = (event) => {
      // Mode 2: Ctrl+Enter (or Cmd+Enter on Mac) for paragraph or selection
      if ((event.ctrlKey || event.metaKey) && !event.altKey && event.key === 'Enter') {
        event.preventDefault();
        executeCode();
      } 
      // Mode 1: Alt+Enter for single line
      else if (event.altKey && !event.ctrlKey && !event.metaKey && event.key === 'Enter') {
        event.preventDefault();
        executeCurrentLine();
      }
      // Mode 1 (Mac): Alt+Cmd+Enter for single line
      else if (event.altKey && event.metaKey && event.key === 'Enter') {
        event.preventDefault();
        executeCurrentLine();
      }
      // Stop music: Ctrl+. or Cmd+. (period)
      else if ((event.ctrlKey || event.metaKey) && event.key === '.') {
        event.preventDefault();
        stopMusic();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    
    // Clean up on unmount
    return () => {
      unsubscribe();
      document.removeEventListener('keydown', handleKeyDown);
      if (editor) {
        editor.toTextArea(); // Clean up CodeMirror instance
      }
    };
  });
  
  // Get current paragraph - text block without blank lines
  function getCurrentParagraph() {
    const cursor = editor.getCursor();
    const line = cursor.line;
    
    // Find the start of the paragraph
    let startLine = line;
    while (startLine > 0) {
      const prevLine = editor.getLine(startLine - 1);
      if (!prevLine || prevLine.trim() === '') {
        break;
      }
      startLine--;
    }
    
    // Find the end of the paragraph
    let endLine = line;
    const totalLines = editor.lineCount();
    while (endLine < totalLines - 1) {
      const nextLine = editor.getLine(endLine + 1);
      if (!nextLine || nextLine.trim() === '') {
        break;
      }
      endLine++;
    }
    
    // Extract the paragraph text
    const from = { line: startLine, ch: 0 };
    const to = { line: endLine, ch: editor.getLine(endLine).length };
    return editor.getRange(from, to);
  }
  
  // Get current line of code
  function getCurrentLine() {
    const cursor = editor.getCursor();
    return editor.getLine(cursor.line);
  }
  
  // Send code to server and handle results
  function sendCodeToExecute(codeToExecute, executionType = 'paragraph') {
    // Don't execute empty code
    if (!codeToExecute || !codeToExecute.trim()) {
      return;
    }
    
    // Add to console output with execution type indicator
    let executionLabel;
    switch (executionType) {
      case 'line':
        executionLabel = 'line';
        break;
      case 'selection':
        executionLabel = 'selection';
        break;
      case 'all':
        executionLabel = 'all code';
        break;
      default:
        executionLabel = 'paragraph';
    }
    
    addConsoleOutput(`> Executing ${executionLabel}:\n${codeToExecute}`, 'command');
    
    // Create a subscription to listen for execution results
    const unsubscribeExecution = appState.subscribe(state => {
      if (state._lastMessage && state._lastMessage.type === 'code_execution_result') {
        const result = state._lastMessage.data;
        
        // Log the result
        if (result.success) {
          // Add success message to console
          if (result.message && result.message.trim()) {
            addConsoleOutput(result.message, 'success');
          }
        } else {
          // Add error message to console
          if (result.message) {
            addConsoleOutput(`Error: ${result.message}`, 'error');
          }
        }
        
        // Unsubscribe after receiving the result
        unsubscribeExecution();
      }
    });
    
    // Send to server
    sendMessage({
      type: 'execute_code',
      data: {
        code: codeToExecute
      }
    });
    
    // Set a timeout to unsubscribe if no response is received
    setTimeout(() => {
      unsubscribeExecution();
    }, 10000); // 10 seconds timeout
  }
  
  // Execute code - Mode 2 (default): Current paragraph or selection
  function executeCode() {
    // Check if the editor is initialized
    if (!editor) {
      console.error("CodeMirror editor not initialized!");
      return;
    }
    
    // Get current selection or current paragraph if nothing is selected
    let codeToExecute;
    let executionType;
    
    if (editor.somethingSelected()) {
      codeToExecute = editor.getSelection();
      executionType = 'selection';
    } else {
      codeToExecute = getCurrentParagraph();
      executionType = 'paragraph';
    }
    
    sendCodeToExecute(codeToExecute, executionType);
  }
  
  // Execute current line - Mode 1: Alt+Enter
  function executeCurrentLine() {
    // Check if the editor is initialized
    if (!editor) {
      console.error("CodeMirror editor not initialized!");
      return;
    }
    
    const currentLine = getCurrentLine();
    sendCodeToExecute(currentLine, 'line');
  }
  
  // Add message to console output
  function addConsoleOutput(message, level = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    
    // Update local console output
    consoleOutput = [
      ...consoleOutput,
      {
        timestamp,
        level,
        message
      }
    ];
    
    // Limit console output to 1000 entries
    if (consoleOutput.length > 1000) {
      consoleOutput = consoleOutput.slice(consoleOutput.length - 1000);
    }
    
    // Update store
    appState.update(state => ({
      ...state,
      consoleOutput
    }));
    
    // Scroll to bottom
    scrollToBottom();
  }
  
  // Clear console
  function clearConsole() {
    consoleOutput = [];
    appState.update(state => ({
      ...state,
      consoleOutput: []
    }));
  }
  
  // Handle editor mount event
  function handleEditorMount(e) {
    editor = e.detail.editor;
  }
  
  // Stop all music playback
  function stopMusic() {
    // Add to console output to show we're stopping music
    addConsoleOutput("Stopping all music playback...", 'command');
    
    // Send the Clock.clear() command to stop all patterns
    sendMessage({
      type: 'execute_code',
      data: {
        code: 'Clock.clear()'
      }
    });
  }</script>

<main>
  <div class="editor-container">
    <header class="editor-header">
      <h1>Renardo Live Coding Editor</h1>
      <div class="shortcuts-info">
        <span class="shortcut-item">Alt+Enter: Run current line</span>
        <span class="shortcut-item">Ctrl+Enter: Run paragraph or selection</span>
        <span class="shortcut-item">Ctrl+.: Stop all music</span>
        <span class="shortcut-item">Run Code button: Run all code</span>
      </div>
      
      <!-- Controls -->
      <div class="editor-controls">
        <button 
          class="execute-button" 
          on:click={() => sendCodeToExecute(editor.getValue(), 'all')} 
          title="Run all code in editor"
        >
          Run Code
        </button>
        <button 
          class="stop-button" 
          on:click={stopMusic}
          title="Stop all music playback"
        >
          Stop Music
        </button>
        <button 
          class="clear-button" 
          on:click={clearConsole}
          title="Clear console output"
        >
          Clear Console
        </button>
      </div>
    </header>
    
    <div class="editor-workspace">
      <!-- Code editor -->
      <div class="code-editor-wrapper" bind:this={editorContainer}>
        <textarea id="code-editor">{editorContent}</textarea>
      </div>
      
      <!-- Console output -->
      <div class="console-wrapper">
        <div class="console-header">
          <h3>Console Output</h3>
        </div>
        <div class="console-output" bind:this={consoleContainer}>
          {#if consoleOutput.length === 0}
            <p class="console-empty">No output yet. Run some code to see results here.</p>
          {:else}
            {#each consoleOutput as output}
              <div class="console-entry console-level-{output.level.toLowerCase()}">
                <span class="console-timestamp">[{output.timestamp}]</span>
                <span class="console-message">{output.message}</span>
              </div>
            {/each}
          {/if}
        </div>
      </div>
    </div>
    
    <!-- Error messages -->
    {#if $appState.error}
      <div class="error-message">
        Error: {$appState.error}
      </div>
    {/if}
  </div>
</main>

<style>
  main {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    padding: 0;
    margin: 0;
    overflow: hidden;
  }
  
  .editor-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    background-color: #f5f5f5;
  }
  
  .editor-header {
    background-color: #2c3e50;
    color: white;
    padding: 1rem;
    display: flex;
    flex-direction: column;
  }
  
  .editor-header h1 {
    margin: 0;
    font-size: 1.5rem;
    margin-bottom: 0.25rem;
  }
  
  .shortcuts-info {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.8rem;
    color: #e0e0e0;
  }
  
  .shortcut-item {
    background-color: rgba(255, 255, 255, 0.1);
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
  }
  
  
  .runtime-status {
    display: flex;
  }
  
  .runtime-running {
    background-color: #4caf50;
  }
  
  .runtime-stopped {
    background-color: #f44336;
  }
  
  .editor-controls {
    display: flex;
    gap: 0.5rem;
  }
  
  button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  button:hover:not(:disabled) {
    background-color: #2980b9;
  }
  
  button:active:not(:disabled) {
    transform: translateY(1px);
  }
  
  button:disabled {
    background-color: #e0e0e0;
    color: #9e9e9e;
    cursor: not-allowed;
  }
  
  
  .execute-button {
    background-color: #27ae60;
  }
  
  .execute-button:hover:not(:disabled) {
    background-color: #219653;
  }
  
  .stop-button {
    background-color: #e67e22;
  }
  
  .stop-button:hover:not(:disabled) {
    background-color: #d35400;
  }
  
  .clear-button {
    background-color: #e74c3c;
  }
  
  .clear-button:hover:not(:disabled) {
    background-color: #c0392b;
  }
  
  .editor-workspace {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
  }
  
  @media (min-width: 992px) {
    .editor-workspace {
      flex-direction: row;
    }
  }
  
  .code-editor-wrapper {
    flex: 1;
    height: 100%;
    min-height: 300px;
    border: 1px solid #e0e0e0;
    overflow: hidden;
  }
  
  .console-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 200px;
    max-height: 100%;
    border: 1px solid #e0e0e0;
    background-color: #1e1e1e;
    color: #f0f0f0;
  }
  
  @media (min-width: 992px) {
    .code-editor-wrapper, .console-wrapper {
      max-width: 50%;
    }
  }
  
  .console-header {
    background-color: #333;
    padding: 0.5rem;
    border-bottom: 1px solid #444;
  }
  
  .console-header h3 {
    margin: 0;
    font-size: 1rem;
  }
  
  .console-output {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
    font-family: monospace;
    font-size: 0.9rem;
  }
  
  .console-entry {
    padding: 0.25rem 0;
    border-bottom: 1px solid #333;
    white-space: pre-wrap;
  }
  
  .console-entry:last-child {
    border-bottom: none;
  }
  
  .console-timestamp {
    color: #888;
    margin-right: 0.5rem;
  }
  
  .console-level-info {
    color: #64b5f6;
  }
  
  .console-level-command {
    color: #80cbc4;
  }
  
  .console-level-error {
    color: #ef5350;
  }
  
  .console-level-success {
    color: #81c784;
  }
  
  .console-level-warn {
    color: #ffb74d;
  }
  
  .console-empty {
    color: #888;
    text-align: center;
    font-style: italic;
    padding: 1rem;
  }
  
  .error-message {
    background-color: #ffebee;
    color: #c62828;
    padding: 0.75rem;
    border-top: 1px solid #ffcdd2;
  }
  
  /* Make CodeMirror look better */
  :global(.CodeMirror) {
    height: 100% !important;
    width: 100%;
    font-family: 'Fira Code', 'Menlo', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.5;
  }
  
  :global(.CodeMirror-gutters) {
    border-right: 1px solid #ddd;
    background-color: #f7f7f7;
  }
  
  :global(.CodeMirror-linenumber) {
    color: #999;
  }
  
  /* Make sure the textarea is hidden properly */
  #code-editor {
    display: none;
  }
</style>