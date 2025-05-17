<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade } from 'svelte/transition';
  import { appState, initWebSocket, sendMessage } from './lib/websocket.js';
  import CodeMirrorThemeSelector from './lib/CodeMirrorThemeSelector.svelte';
  // We'll load CodeMirror and its dependencies from CDN
  
  // State for right panel
  let rightPanelOpen = true;
  let activeTab = 'tutorial'; // tutorial, sessions, musicExamples, or documentation
  
  // Tutorial files state
  let tutorialFiles = [];
  let loadingTutorials = false;
  
  // Session files state
  let sessionFiles = [];
  let loadingSessions = false;
  
  // Save session modal state
  let showSaveModal = false;
  let sessionName = '';
  let savingSession = false;
  
  // Initialization check
  let showInitModal = false;
  let initStatus = {
    superColliderClasses: false,
    sclangCode: false,
    samples: false,
    instruments: false
  };
  let modalDismissed = false;
  
  // State for multi-tab editor
  let tabs = [
    {
      id: 1,
      name: 'Buffer 1',
      content: `# Renardo Live Coding Editor
# Type your code here and press Ctrl+Enter to run

Root.default = var([0,2,4], [2,4,6])
d1 >> play("<x-(-[--])><*....><..(ooo(oO)).>")
d2 >> blip([2,_,[4,4,4,P*(5,2)],_], dur=.5, sus=linvar([.2,.5,3],16), pan=[-.8,0,.8]).eclipse(4,16)
d3 >> pluck(dur=.25, oct=3, sus=linvar([.2,.5,3],16), amp=[.7,.7,1,2], lpf=linvar([400,600,3000],16)).eclipse(16,96)
k2 >> play("V.", lpf=400).eclipse(64,128)

d2.dur=var([.25,1/3,1/2], 16)

Master().fadeout(dur=24)
`
    }
  ];
  
  let activeTabId = 1;
  let nextTabId = 2;
  
  // Get the active tab's content
  $: activeBuffer = tabs.find(t => t.id === activeTabId);
  $: editorContent = activeBuffer ? activeBuffer.content : '';
  
  // Watch for buffer switches and update editor
  $: if (editor && activeBuffer) {
    if (editor.getValue() !== activeBuffer.content) {
      editor.setValue(activeBuffer.content);
    }
  }

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
            const currentBuffer = tabs.find(t => t.id === activeTabId);
            if (currentBuffer) {
              currentBuffer.content = instance.getValue();
              tabs = tabs; // Trigger reactivity
            }
          });

          // Add key bindings for different execution modes
          editor.setOption('extraKeys', {
            'Ctrl-Enter': executeCode,       // Mode 2: Execute paragraph or selection
            'Cmd-Enter': executeCode,        // For Mac
            'Alt-Enter': executeCurrentLine, // Mode 1: Execute current line
            'Alt-Cmd-Enter': executeCurrentLine // For Mac Alt+Enter
            // Note: Ctrl+. and Cmd+. are handled by the document listener
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
    
    // Load tutorial files on mount since panel is open by default
    loadTutorialFiles();
    
    // Subscribe to appState changes to update UI
    const unsubscribe = appState.subscribe(state => {
      // Update console output
      if (state.consoleOutput && state.consoleOutput.length > 0) {
        // We're just using the store's version of the console output
        consoleOutput = state.consoleOutput;

        // Check if we should scroll
        // With this approach, we'll scroll when anything changes
        // If more fine-grained control is needed, we could store a timestamp
        scrollToBottom();
      }
      
      // Check initialization status
      if (state.renardoInit) {
        initStatus = {
          superColliderClasses: state.renardoInit.superColliderClasses === true,
          sclangCode: state.renardoInit.sclangCode === true,
          samples: state.renardoInit.samples === true,
          instruments: state.renardoInit.instruments === true
        };
        
        // Check if any initialization steps are incomplete
        const atLeastOneIncomplete = Object.values(initStatus).some(status => status === false);
        
        // Only show the modal if at least one step is incomplete and the modal hasn't been dismissed
        if (atLeastOneIncomplete && !modalDismissed) {
          showInitModal = true;
        } else {
          showInitModal = false;
        }
      }
    });
    
    // Set up keyboard shortcuts for execution - fallback for whole document
    const handleKeyDown = (event) => {
      // Stop music should work regardless of focus
      if ((event.ctrlKey || event.metaKey) && event.key === '.') {
        event.preventDefault();
        stopMusic();
        return;
      }
      
      // Only handle other key events when CodeMirror doesn't have focus
      if (editor && editor.hasFocus()) {
        return; // Let CodeMirror handle it
      }
      
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
  }
  
  // Initialize helper functions
  function dismissInitModal() {
    showInitModal = false;
    modalDismissed = true;
    
    // Add a warning message to the console if initialization steps are incomplete
    const missingSteps = [];
    if (!initStatus.superColliderClasses) missingSteps.push("SuperCollider Classes");
    if (!initStatus.sclangCode) missingSteps.push("SCLang Code");
    if (!initStatus.samples) missingSteps.push("Sample Packs");
    if (!initStatus.instruments) missingSteps.push("Instruments & Effects");
    
    if (missingSteps.length > 0) {
      // Add console output for warning about incomplete initialization
      addConsoleOutput(
        `⚠️ Warning: Some initialization steps are incomplete (${missingSteps.join(", ")}). Some features may not work properly.`,
        'warn'
      );
    }
  }
  
  function goToInitializePage() {
    window.location.hash = 'init';
  }
  
  // Function to add a new buffer
  function addNewBuffer() {
    const newBuffer = {
      id: nextTabId++,
      name: `Buffer ${tabs.length + 1}`,
      content: '# New buffer\n'
    };
    tabs = [...tabs, newBuffer];
    activeTabId = newBuffer.id;
  }
  
  // Function to close a buffer
  function closeBuffer(bufferId) {
    if (tabs.length <= 1) return; // Keep at least one buffer
    
    tabs = tabs.filter(t => t.id !== bufferId);
    
    // If we closed the active buffer, switch to another one
    if (activeTabId === bufferId) {
      activeTabId = tabs[0].id;
    }
  }
  
  // Function to insert preset code at cursor position
  function insertPreset(code) {
    if (!editor) return;
    
    const cursor = editor.getCursor();
    editor.replaceRange(code + '\n', cursor);
    editor.setCursor({ line: cursor.line + code.split('\n').length, ch: 0 });
    editor.focus();
  }
  
  // Function to load tutorial files
  async function loadTutorialFiles() {
    loadingTutorials = true;
    try {
      const response = await fetch('/api/tutorial/files');
      if (response.ok) {
        const data = await response.json();
        tutorialFiles = data.files || [];
      } else {
        console.error('Failed to load tutorial files');
        tutorialFiles = [];
      }
    } catch (error) {
      console.error('Error loading tutorial files:', error);
      tutorialFiles = [];
    } finally {
      loadingTutorials = false;
    }
  }
  
  // Function to load a tutorial file into the editor
  async function loadTutorialFile(file) {
    try {
      const response = await fetch(file.url);
      if (response.ok) {
        const content = await response.text();
        // Create a new buffer for the tutorial
        const newBuffer = {
          id: nextTabId++,
          name: file.name.replace('.py', ''),
          content: content
        };
        tabs = [...tabs, newBuffer];
        activeTabId = newBuffer.id;
        
        if (editor) {
          editor.setValue(content);
          editor.setCursor({ line: 0, ch: 0 });
          editor.focus();
        }
      } else {
        console.error('Failed to load tutorial file');
      }
    } catch (error) {
      console.error('Error loading tutorial file:', error);
    }
  }
  
  // Function to open save session modal
  function saveSession() {
    showSaveModal = true;
    sessionName = '';
  }
  
  // Function to actually save the session
  async function doSaveSession() {
    if (!sessionName.trim()) return;
    
    savingSession = true;
    try {
      // Concatenate all buffers with separator
      const separator = '#'.repeat(80) + '\n';
      const combinedContent = tabs
        .map(tab => tab.content)
        .join('\n' + separator + '\n');
      
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          filename: sessionName,
          content: combinedContent
        })
      });
      
      const result = await response.json();
      if (result.success) {
        showSaveModal = false;
        sessionName = '';
        
        // Show success message in console
        addConsoleOutput(`Session saved as ${result.filename}`, 'success');
        
        // Reload sessions list if the sessions tab is active
        if (activeTab === 'sessions') {
          loadSessionFiles();
        }
      } else {
        alert(`Failed to save session: ${result.message}`);
      }
    } catch (error) {
      console.error('Error saving session:', error);
      alert('Error saving session');
    } finally {
      savingSession = false;
    }
  }
  
  // Function to cancel save session
  function cancelSaveSession() {
    showSaveModal = false;
    sessionName = '';
    savingSession = false;
  }
  
  // Function to load a session
  async function loadSession() {
    // Switch to sessions tab and load list
    rightPanelOpen = true;
    activeTab = 'sessions';
    loadSessionFiles();
  }
  
  // Function to load session files list
  async function loadSessionFiles() {
    loadingSessions = true;
    try {
      const response = await fetch('/api/sessions');
      if (response.ok) {
        const data = await response.json();
        sessionFiles = data.sessions || [];
      } else {
        console.error('Failed to load session files');
        sessionFiles = [];
      }
    } catch (error) {
      console.error('Error loading session files:', error);
      sessionFiles = [];
    } finally {
      loadingSessions = false;
    }
  }
  
  // Function to load a session file into the editor
  async function loadSessionFile(file) {
    try {
      const response = await fetch(file.url);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Split content by separator
          const separator = '#'.repeat(80);
          const bufferContents = data.content.split(new RegExp(`\\n?${separator}\\n?`));
          
          // Clear existing tabs and create new ones from the loaded content
          tabs = [];
          let newTabId = 1;
          
          bufferContents.forEach((content, index) => {
            if (content.trim()) { // Only create buffer if content is not empty
              tabs.push({
                id: newTabId++,
                name: `Buffer ${index + 1}`,
                content: content
              });
            }
          });
          
          // If no buffers were created, create at least one
          if (tabs.length === 0) {
            tabs.push({
              id: 1,
              name: 'Buffer 1',
              content: ''
            });
          }
          
          // Set the first buffer as active
          activeTabId = tabs[0].id;
          nextTabId = newTabId;
          
          // Update editor with first buffer's content
          if (editor) {
            editor.setValue(tabs[0].content);
            editor.setCursor({ line: 0, ch: 0 });
            editor.focus();
          }
        } else {
          console.error('Failed to load session file:', data.message);
        }
      } else {
        console.error('Failed to load session file');
      }
    } catch (error) {
      console.error('Error loading session file:', error);
    }
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

          <button
            class="btn btn-sm btn-primary"
            on:click={saveSession}
            title="Save current code as a session"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            Save Session
          </button>

          <button
            class="btn btn-sm btn-primary"
            on:click={loadSession}
            title="Load a saved session"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            Load Session
          </button>
        </div>

        <!-- Right Panel Toggle and Editor Theme Selector -->
        <div class="flex items-center gap-2">
          <button
            class="btn btn-sm btn-outline"
            on:click={() => {
              rightPanelOpen = !rightPanelOpen;
              if (!rightPanelOpen) return;
              // Reload files when opening the panel
              if (activeTab === 'tutorial') {
                loadTutorialFiles();
              } else if (activeTab === 'sessions') {
                loadSessionFiles();
              }
            }}
            title="{rightPanelOpen ? 'Close' : 'Open'} side panel"
          >
            {#if rightPanelOpen}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clip-rule="evenodd" />
              </svg>
            {/if}
            {rightPanelOpen ? 'Hide' : 'Show'} Panel
          </button>
          <CodeMirrorThemeSelector bind:editor={editor} />
        </div>
      </div>
    </div>
  </div>

  <!-- Buffer tabs -->
  <div class="bg-base-200 px-4 pt-2 pb-0">
    <div class="flex items-center gap-1">
      {#each tabs as buffer}
        <button
          class="tab tab-lifted {activeTabId === buffer.id ? 'tab-active' : ''}"
          on:click={() => activeTabId = buffer.id}
        >
          {buffer.name}
          {#if tabs.length > 1}
            <button
              class="ml-2 btn btn-xs btn-circle btn-ghost"
              on:click|stopPropagation={() => closeBuffer(buffer.id)}
            >
              ×
            </button>
          {/if}
        </button>
      {/each}
      <button
        class="tab tab-lifted"
        on:click={addNewBuffer}
        title="New Buffer"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </div>

  <!-- Main workspace -->
  <div class="flex flex-1 overflow-hidden">
    <!-- Left side: Code editor and console -->
    <div class="flex flex-col flex-1 overflow-hidden">
      <!-- Code editor -->
      <div class="flex-1 border border-base-300" bind:this={editorContainer}>
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

    <!-- Right side: Collapsible panel with tabs -->
    {#if rightPanelOpen}
      <div transition:fade={{ duration: 200 }} class="w-96 flex flex-col border-l border-base-300 bg-base-100 transition-all">
        <!-- Panel header with tabs and close button -->
        <div class="bg-base-300 p-2">
          <div class="flex justify-between items-center mb-2">
            <div class="tabs tabs-boxed">
              <button 
                class="tab {activeTab === 'tutorial' ? 'tab-active' : ''}" 
                on:click={() => activeTab = 'tutorial'}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                Tutorial
              </button>
              <button 
                class="tab {activeTab === 'sessions' ? 'tab-active' : ''}" 
                on:click={() => {activeTab = 'sessions'; loadSessionFiles();}}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clip-rule="evenodd" />
                </svg>
                Sessions
              </button>
              <button 
                class="tab {activeTab === 'musicExamples' ? 'tab-active' : ''}" 
                on:click={() => activeTab = 'musicExamples'}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
                </svg>
                Music Examples
              </button>
              <button 
                class="tab {activeTab === 'documentation' ? 'tab-active' : ''}" 
                on:click={() => activeTab = 'documentation'}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                </svg>
                Documentation
              </button>
            </div>
            <button
              class="btn btn-sm btn-ghost btn-square"
              on:click={() => rightPanelOpen = false}
              title="Close panel"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Tab content -->
        <div class="flex-1 overflow-y-auto p-4">
          {#if activeTab === 'tutorial'}
            <div>
              <h3 class="text-lg font-bold mb-4">Tutorials</h3>
              {#if loadingTutorials}
                <div class="flex justify-center">
                  <span class="loading loading-spinner loading-md"></span>
                </div>
              {:else if tutorialFiles.length === 0}
                <p class="text-sm opacity-70">No tutorial files available.</p>
              {:else}
                <div class="space-y-2">
                  {#each tutorialFiles as file}
                    <button
                      class="w-full text-left btn btn-sm btn-outline justify-start"
                      on:click={() => loadTutorialFile(file)}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clip-rule="evenodd" />
                      </svg>
                      {file.name}
                    </button>
                  {/each}
                </div>
              {/if}
            </div>
          {:else if activeTab === 'musicExamples'}
            <div>
              <h3 class="text-lg font-bold mb-4">Music Examples</h3>
              <p class="text-sm opacity-70">Coming soon...</p>
            </div>
          {:else if activeTab === 'sessions'}
            <div>
              <h3 class="text-lg font-bold mb-4">Sessions</h3>
              {#if loadingSessions}
                <div class="flex justify-center">
                  <span class="loading loading-spinner loading-md"></span>
                </div>
              {:else if sessionFiles.length === 0}
                <p class="text-sm opacity-70">No saved sessions yet.</p>
              {:else}
                <div class="space-y-2">
                  {#each sessionFiles as file}
                    <button
                      class="w-full text-left btn btn-sm btn-outline justify-start"
                      on:click={() => loadSessionFile(file)}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clip-rule="evenodd" />
                      </svg>
                      {file.name}
                    </button>
                  {/each}
                </div>
              {/if}
            </div>
          {:else if activeTab === 'documentation'}
            <div>
              <h3 class="text-lg font-bold mb-4">Renardo Documentation</h3>
              <div class="prose">
                <h4 class="text-md font-semibold mb-2">Quick Start</h4>
                <p class="text-sm mb-4">
                  Renardo is a Python-based live coding environment for creating music in real-time.
                </p>
                
                <h4 class="text-md font-semibold mb-2">Basic Commands</h4>
                <ul class="text-sm space-y-2">
                  <li><code class="bg-base-300 px-2 py-1 rounded">d1 >> play("x-o-")</code> - Play a drum pattern</li>
                  <li><code class="bg-base-300 px-2 py-1 rounded">p1 >> pluck([0,2,4,7])</code> - Play a melody</li>
                  <li><code class="bg-base-300 px-2 py-1 rounded">p1.stop()</code> - Stop a player</li>
                  <li><code class="bg-base-300 px-2 py-1 rounded">Clock.clear()</code> - Stop all patterns</li>
                </ul>
                
                <h4 class="text-md font-semibold mt-4 mb-2">Keyboard Shortcuts</h4>
                <ul class="text-sm space-y-1">
                  <li><kbd class="kbd kbd-sm">Alt+Enter</kbd> - Execute current line</li>
                  <li><kbd class="kbd kbd-sm">Ctrl+Enter</kbd> - Execute paragraph or selection</li>
                  <li><kbd class="kbd kbd-sm">Ctrl+.</kbd> - Stop all music</li>
                </ul>
              </div>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>

  <!-- Error messages -->
  {#if $appState.error}
    <div class="alert alert-error rounded-none">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
      <span>Error: {$appState.error}</span>
    </div>
  {/if}
</div>

<!-- Initialization Modal -->
{#if showInitModal}
  <div class="modal modal-open" transition:fade={{ duration: 200 }}>
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">Setup Required</h3>
      <div class="flex flex-col items-center mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-warning mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-center mb-4">Some initialization steps are not complete.</p>
        
        <div class="w-full space-y-2 mb-4">
          <div class="flex items-center">
            <div class="w-6 h-6 mr-2">
              {#if initStatus.superColliderClasses}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {/if}
            </div>
            <span class="{initStatus.superColliderClasses ? 'text-success' : 'text-error'}">SuperCollider Classes</span>
          </div>
          
          <div class="flex items-center">
            <div class="w-6 h-6 mr-2">
              {#if initStatus.sclangCode}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {/if}
            </div>
            <span class="{initStatus.sclangCode ? 'text-success' : 'text-error'}">SCLang Code</span>
          </div>
          
          <div class="flex items-center">
            <div class="w-6 h-6 mr-2">
              {#if initStatus.samples}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {/if}
            </div>
            <span class="{initStatus.samples ? 'text-success' : 'text-error'}">Sample Packs</span>
          </div>
          
          <div class="flex items-center">
            <div class="w-6 h-6 mr-2">
              {#if initStatus.instruments}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {/if}
            </div>
            <span class="{initStatus.instruments ? 'text-success' : 'text-error'}">Instruments & Effects</span>
          </div>
        </div>
        
        <p class="text-center text-sm opacity-75">Complete the initialization steps to ensure Renardo works properly.</p>
      </div>
      <div class="flex flex-col gap-2">
        <button class="btn btn-primary" on:click={goToInitializePage}>Go to Initialize Page</button>
        <button class="btn btn-outline" on:click={dismissInitModal}>Continue Anyway</button>
      </div>
    </div>
  </div>
{/if}

<!-- Save Session Modal -->
{#if showSaveModal}
  <div class="modal modal-open" transition:fade={{ duration: 200 }}>
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">Save Session</h3>
      
      <div class="form-control">
        <label for="session-name-input" class="label">
          <span class="label-text">Session Name</span>
        </label>
        <input 
          id="session-name-input"
          type="text" 
          placeholder="my_session.py" 
          class="input input-bordered w-full"
          bind:value={sessionName}
          on:keydown={(e) => {
            if (e.key === 'Enter' && sessionName.trim()) {
              doSaveSession();
            } else if (e.key === 'Escape') {
              cancelSaveSession();
            }
          }}
          disabled={savingSession}
        />
        <label for="session-name-input" class="label">
          <span class="label-text-alt">The .py extension will be added automatically if not provided</span>
        </label>
      </div>
      
      <div class="modal-action">
        <button 
          class="btn btn-primary"
          on:click={doSaveSession}
          disabled={!sessionName.trim() || savingSession}
        >
          {#if savingSession}
            <span class="loading loading-spinner loading-sm"></span>
            Saving...
          {:else}
            Save
          {/if}
        </button>
        <button 
          class="btn btn-outline"
          on:click={cancelSaveSession}
          disabled={savingSession}
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  /* Style for buffer tabs */
  .tab-lifted {
    padding: 0.5rem 1rem;
    margin-right: 0.25rem;
    font-size: 0.875rem;
  }
  
  .tab-active {
    background-color: oklch(var(--b1));
  }
  
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
  
  /* Smooth transitions for layout changes */
  .flex {
    transition: all 0.3s ease;
  }
</style>