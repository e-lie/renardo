<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade } from 'svelte/transition';
  import { appState, initWebSocket, sendMessage } from './lib/websocket.js';
  // We'll load CodeMirror from CDN instead
  
  // State for editor content
  let editorContent = `# Renardo Live Coding Editor
# Type your code here and press Ctrl+Enter to run

d1 >> play("x-o-").every(4, "stutter", 4)
d2 >> play("  * ").speed(2)
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
  
  // WebSocket check
  const webSocketSupported = 'WebSocket' in window;
  
  // Function to scroll console to bottom
  function scrollToBottom() {
    if (consoleContainer) {
      setTimeout(() => {
        consoleContainer.scrollTop = consoleContainer.scrollHeight;
      }, 50);
    }
  }
  
  // Initialize WebSocket connection and CodeMirror on mount
  onMount(() => {
    if (webSocketSupported) {
      initWebSocket();
      
      // Wait for CodeMirror to be loaded from CDN 
      const initEditor = () => {
        if (typeof window.CodeMirror === 'undefined') {
          // If CodeMirror isn't loaded yet, try again in 100ms
          setTimeout(initEditor, 100);
          return;
        }
        
        // Initialize CodeMirror
        const codeMirrorOptions = {
          value: editorContent,
          lineNumbers: true,
          mode: 'python',
          theme: 'monokai',
          tabSize: 4,
          indentWithTabs: false,
          indentUnit: 4,
          lineWrapping: true,
          viewportMargin: Infinity
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
          
          // Add key binding for Ctrl+Enter to execute code
          editor.setOption('extraKeys', {
            'Ctrl-Enter': executeCode,
            'Cmd-Enter': executeCode // For Mac
          });
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
      
      // Set up keyboard shortcut for execution (Ctrl+Enter) - fallback for whole document
      const handleKeyDown = (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
          event.preventDefault();
          executeCode();
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
    }
  });
  
  // Execute code
  function executeCode() {
    // Check if the editor is initialized
    if (!editor) {
      console.error("CodeMirror editor not initialized!");
      return;
    }
    
    // Get current selection or all text if nothing is selected
    let codeToExecute;
    if (editor.somethingSelected()) {
      codeToExecute = editor.getSelection();
    } else {
      codeToExecute = editor.getValue();
    }
    
    // Don't execute empty code
    if (!codeToExecute.trim()) {
      return;
    }
    
    // Add to console output
    addConsoleOutput(`> Executing code:\n${codeToExecute}`, 'command');
    
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
  
  // Go back to init page
  function goToInit() {
    window.location.hash = '#init';
  }
</script>

<main>
  <div class="editor-container">
    <header class="editor-header">
      <h1>Renardo Live Coding Editor</h1>
      
      <!-- Connection status -->
      <div class="status-bar">
        {#if webSocketSupported}
          {#if $appState.connected}
            <div class="status-indicator connected" transition:fade={{ duration: 300 }}>
              Connected
            </div>
          {:else}
            <div class="status-indicator" transition:fade={{ duration: 300 }}>
              Disconnected
            </div>
          {/if}
        {:else}
          <div class="status-indicator fallback">
            Using HTTP Fallback (WebSockets not supported)
          </div>
        {/if}
      </div>
      
      <!-- Controls -->
      <div class="editor-controls">
        <button 
          class="execute-button" 
          on:click={executeCode} 
          title="Run code (Ctrl+Enter)"
        >
          Run Code
        </button>
        <button 
          class="clear-button" 
          on:click={clearConsole}
          title="Clear console output"
        >
          Clear Console
        </button>
        <button 
          class="init-button" 
          on:click={goToInit}
          title="Go back to initialization page"
        >
          Back to Init
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
    margin-bottom: 0.5rem;
  }
  
  .status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  
  .status-indicator {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    background-color: #f44336;
    color: white;
    margin-right: 0.5rem;
  }
  
  .status-indicator.connected {
    background-color: #4caf50;
  }
  
  .status-indicator.fallback {
    background-color: #ff9800;
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
  
  .clear-button {
    background-color: #e74c3c;
  }
  
  .clear-button:hover:not(:disabled) {
    background-color: #c0392b;
  }
  
  .init-button {
    background-color: #9b59b6;
  }
  
  .init-button:hover:not(:disabled) {
    background-color: #8e44ad;
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