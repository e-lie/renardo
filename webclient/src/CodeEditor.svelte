<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade } from 'svelte/transition';
  import { appState, initWebSocket, sendMessage } from './lib/websocket.js';
  import CodeMirrorThemeSelector from './lib/CodeMirrorThemeSelector.svelte';
  // We'll load CodeMirror and its dependencies from CDN
  
  // State for editor content
  let editorContent = `# Renardo Live Coding Editor
# Type your code here and press Ctrl+Enter to run

Root.default = var([0,2,4], [2,4,6])
d1 >> play("<x-(-[--])><*....><..(ooo(oO)).>")
d2 >> blip([2,_,[4,4,4,P*(5,2)],_], dur=.5, sus=linvar([.2,.5,3],16), pan=[-.8,0,.8]).eclipse(4,16)
d3 >> pluck(dur=.25, oct=3, sus=linvar([.2,.5,3],16), amp=[.7,.7,1,2], lpf=linvar([400,600,3000],16)).eclipse(16,96)
k2 >> play("V.", lpf=400).eclipse(64,128)

d2.dur=var([.25,1/3,1/2], 16)

Master().fadeout(dur=24)
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
        // Check if the script is already loaded
        const existingScript = document.querySelector(`script[src="${src}"]`);
        if (existingScript) {
          resolve();
          return;
        }

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

        // Load our local Dracula theme CSS
        await loadCSS('/codemirror-themes/dracula.css');
        
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
          theme: 'dracula',
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

          // For the editor to be properly initialized with the theme and settings,
          // we need to make sure we're using the right settings from local storage
          const savedTheme = localStorage.getItem('editor-theme') || 'dracula';
          const showLineNumbers = localStorage.getItem('editor-show-line-numbers') !== 'false';
          const vimModeEnabled = localStorage.getItem('editor-vim-mode') === 'true';

          // Apply basic settings
          editor.setOption('theme', savedTheme);
          editor.setOption('lineNumbers', showLineNumbers);

          // Handle Vim mode if enabled
          if (vimModeEnabled) {
            // Load Vim mode script
            loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/keymap/vim.min.js').then(() => {
              if (window.CodeMirror.Vim) {
                // Add a common escape mapping
                window.CodeMirror.Vim.map('jk', '<Esc>', 'insert');
                // Set the keymap to Vim
                editor.setOption('keyMap', 'vim');
              }
            }).catch(err => {
              console.error('Failed to load Vim mode:', err);
              localStorage.setItem('editor-vim-mode', 'false');
            });
          }

          // Refresh the editor to apply all settings
          setTimeout(() => {
            editor.refresh();
          }, 100);
          
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
    
    // Subscribe to appState changes to update UI
    const unsubscribe = appState.subscribe(state => {
      if (state.consoleOutput && state.consoleOutput.length > 0) {
        // We're just using the store's version of the console output
        consoleOutput = state.consoleOutput;

        // Check if we should scroll
        // With this approach, we'll scroll when anything changes
        // If more fine-grained control is needed, we could store a timestamp
        scrollToBottom();
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

    // Don't add the command to the console output
    // Just send the command to the server for execution
    // The server will return the result which will be displayed

    // Send to server with unique request ID to prevent duplicate execution
    sendMessage({
      type: 'execute_code',
      data: {
        code: codeToExecute,
        requestId: Date.now() // Add unique ID to prevent duplicates
      }
    });
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
  
  // This is now a local helper function for UI-only actions (not for code execution)
  // Used for things like clearing the console, not for adding execution output
  function addConsoleOutput(message, level = 'info') {
    const timestamp = new Date().toLocaleTimeString();

    // Log the operation but don't update local state AND global state to avoid duplication
    // Update the store only
    appState.update(state => {
      const entry = {
        timestamp,
        level,
        message
      };

      const updatedConsoleOutput = [...state.consoleOutput, entry];
      // Limit console output to 1000 entries
      const trimmedConsoleOutput = updatedConsoleOutput.slice(-1000);

      return {
        ...state,
        consoleOutput: trimmedConsoleOutput
      };
    });

    // Scroll to bottom
    scrollToBottom();
  }
  
  // Clear console
  function clearConsole() {
    // Only need to update the store
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
    // Don't add a console message, just send the command

    // Send the Clock.clear() command to stop all patterns with a unique request ID
    sendMessage({
      type: 'execute_code',
      data: {
        code: 'Clock.clear()',
        requestId: Date.now() // Add unique ID to prevent duplicates
      }
    });
  }</script>

<div class="flex flex-col h-screen w-full overflow-hidden">
  <!-- Header with controls -->
  <div class="bg-base-300 p-4">
    <div class="flex flex-col gap-2">
      <div class="flex flex-wrap gap-2 text-xs mb-2">
        <span class="badge badge-sm">Alt+Enter: Run current line</span>
        <span class="badge badge-sm">Ctrl+Enter: Run paragraph or selection</span>
        <span class="badge badge-sm">Ctrl+.: Stop all music</span>
        <span class="badge badge-sm">Run Code button: Run all code</span>
      </div>

      <div class="flex flex-wrap justify-between items-center gap-2">
        <div class="flex flex-wrap gap-2">
          <button
            class="btn btn-sm btn-success"
            on:click={() => sendCodeToExecute(editor.getValue(), 'all')}
            title="Run all code in editor"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
            </svg>
            Run Code
          </button>

          <button
            class="btn btn-sm btn-warning"
            on:click={stopMusic}
            title="Stop all music playback"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd" />
            </svg>
            Stop Music
          </button>

          <button
            class="btn btn-sm btn-error"
            on:click={clearConsole}
            title="Clear console output"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            Clear Console
          </button>
        </div>

        <!-- Editor Theme Selector -->
        <CodeMirrorThemeSelector bind:editor={editor} />
      </div>
    </div>
  </div>

  <!-- Main workspace -->
  <div class="flex flex-col flex-1 overflow-hidden">
    <!-- Code editor -->
    <div class="flex-1 min-h-[60vh] border border-base-300" bind:this={editorContainer}>
      <textarea id="code-editor">{editorContent}</textarea>
    </div>

    <!-- Console output - always below editor -->
    <div class="flex flex-col h-[30vh] bg-neutral text-neutral-content overflow-hidden">
      <div class="flex justify-between items-center px-4 py-2 bg-neutral-focus text-neutral-content">
        <h3 class="text-sm font-bold"> ฅ^•ﻌ•^ฅ >> output</h3>
        <button
          class="btn btn-xs btn-ghost"
          on:click={clearConsole}
          title="Clear console output"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          Clear
        </button>
      </div>
      <div class="overflow-y-auto flex-1 p-4 font-mono text-sm" bind:this={consoleContainer}>
        {#if consoleOutput.length === 0}
          <div class="flex items-center justify-center h-full opacity-50 italic">
            No output yet. Run some code to see results here.
          </div>
        {:else}
          {#each consoleOutput as output}
            <div class="mb-1 border-b border-base-300 border-opacity-20 pb-1">
              <span class="{
                output.level.toLowerCase() === 'info' ? 'text-info' :
                output.level.toLowerCase() === 'command' ? 'text-accent font-bold' :
                output.level.toLowerCase() === 'error' ? 'text-error font-bold' :
                output.level.toLowerCase() === 'success' ? 'text-success' :
                output.level.toLowerCase() === 'warn' ? 'text-warning' : ''
              } whitespace-pre-wrap">{output.message}</span>
            </div>
          {/each}
        {/if}
      </div>
    </div>
  </div>

  <!-- Error messages -->
  {#if $appState.error}
    <div class="alert alert-error rounded-none">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
      <span>Error: {$appState.error}</span>
    </div>
  {/if}
</div>

<style>
  /* Make CodeMirror look better */
  :global(.CodeMirror) {
    height: 100% !important;
    width: 100%;
    font-family: 'Fira Code', 'Menlo', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.5;
  }

  /* Let themes handle gutter colors - default theme fallback */
  :global(.CodeMirror-gutters) {
    border-right: 1px solid rgba(0, 0, 0, 0.1);
  }

  :global(.CodeMirror-linenumber) {
    color: inherit;
    opacity: 0.6;
  }

  /* Make sure the textarea is hidden properly */
  #code-editor {
    display: none;
  }
</style>