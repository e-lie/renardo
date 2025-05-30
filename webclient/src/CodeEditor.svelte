<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade, slide } from 'svelte/transition';
  import { appState, initWebSocket, sendMessage } from './lib/websocket.js';
  import CodeMirrorThemeSelector from './lib/CodeMirrorThemeSelector.svelte';
  // We'll load CodeMirror and its dependencies from CDN
  
  // State for right panel
  let rightPanelOpen = true;
  let rightPanelWidth = 384; // Default width in pixels (w-96 = 384px)
  let activeTab = 'tutorial'; // tutorial, sessions, startupFiles, musicExamples, or documentation
  let isResizing = false;
  
  // Documentation state
  let documentationFiles = [];
  let loadingDocumentation = false;
  let currentDocumentationContent = '';
  let selectedDocumentationFile = null;
  
  // Music examples state
  let musicExampleFiles = [];
  let loadingMusicExamples = false;
  
  // State for vertical split between editor and console
  let consoleHeight = 30; // Default console height as percentage of available height
  let isVerticalResizing = false;
  
  // Tutorial files state
  let tutorialFiles = [];
  let loadingTutorials = false;
  let selectedLanguage = 'en';
  let availableLanguages = [];
  
  // Session files state
  let sessionFiles = [];
  let loadingSessions = false;
  
  // Startup files state
  let startupFiles = [];
  let loadingStartupFiles = false;
  let selectedStartupFile = null;
  
  // Save session modal state
  let showSaveModal = false;
  let sessionName = '';
  let savingSession = false;
  
  // New buffer modal state
  let showNewBufferModal = false;
  let newBufferName = '';
  let creatingBuffer = false;
  
  // Close buffer confirmation modal state
  let showCloseBufferModal = false;
  let bufferToClose = null;
  
  // Zen mode state
  let zenMode = false;
  
  // Console minimize state
  let consoleMinimized = false;
  let consoleHeightBeforeMinimize = 30; // Store height before minimizing
  let minimizedConsoleHeight = 15; // Height percentage when minimized (for ~2 lines)
  
  // Code execution highlighting state
  let activeHighlights = new Map(); // Map of requestId -> CodeMirror TextMarker
  
  // Initialization check
  let showInitModal = false;
  let initStatus = {
    superColliderClasses: false,
    sclangCode: false,
    samples: false,
    instruments: false,
    reaperPack: false
  };
  let modalDismissed = false;
  
  // Session state
  let currentSession = {
    name: 'Untitled Session',
    startupFile: null, // Reference to the startup file for this session
    modified: false
  };
  
  // State for multi-tab editor
  let tabs = [];
  
  let activeTabId = 1;
  let nextTabId = 2;
  
  // Get the active tab's content
  $: activeBuffer = tabs.find(t => t.id === activeTabId);
  $: editorContent = activeBuffer ? activeBuffer.content : '';
  
  // Check if there's a startup file tab
  $: startupFileTab = tabs.find(tab => tab.isStartupFile);
  
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
  let currentEditorTheme = "dracula"; // Default theme
  
  // Calculate console colors based on theme
  $: consoleColors = getConsoleColorsForTheme(currentEditorTheme);
  
  // Function to get console colors for a given theme
  function getConsoleColorsForTheme(theme) {
    // Default colors (dark theme)
    let consoleBg = "#21222c";
    let consoleHeaderBg = "#191a21";
    let textColor = "#f8f8f2";
    
    switch(theme) {
      case "dracula":
        consoleBg = "#21222c";
        consoleHeaderBg = "#191a21";
        textColor = "#f8f8f2";
        break;
      case "monokai":
        consoleBg = "#272822";
        consoleHeaderBg = "#1e1f1c";
        textColor = "#f8f8f2";
        break;
      case "material":
        consoleBg = "#263238";
        consoleHeaderBg = "#1c262b";
        textColor = "#eeffff";
        break;
      case "nord":
        consoleBg = "#2e3440";
        consoleHeaderBg = "#272c36";
        textColor = "#d8dee9";
        break;
      case "solarized-dark":
        consoleBg = "#002b36";
        consoleHeaderBg = "#00212b";
        textColor = "#839496";
        break;
      case "solarized-light":
        consoleBg = "#fdf6e3";
        consoleHeaderBg = "#eee8d5";
        textColor = "#657b83";
        break;
      case "darcula":
        consoleBg = "#2b2b2b";
        consoleHeaderBg = "#1e1e1e";
        textColor = "#a9b7c6";
        break;
      case "eclipse":
        consoleBg = "#f7f7f7";
        consoleHeaderBg = "#e7e7e7";
        textColor = "#333";
        break;
      default:
        // Use default dark theme colors
        break;
    }
    
    return { 
      consoleBg, 
      consoleHeaderBg, 
      textColor 
    };
  }
  
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
  // Setup resize event handlers
  function handleMouseMove(e) {
    if (isResizing) {
      // Add class to body during resizing
      document.body.classList.add('resizing');
      
      // Calculate new width based on mouse position
      const containerWidth = document.body.clientWidth;
      const mouseX = e.clientX;
      
      // Ensure the panel has a reasonable width (between 240px and 50% of window)
      const minWidth = 240;
      const maxWidth = containerWidth * 0.5;
      const newWidth = containerWidth - mouseX;
      
      rightPanelWidth = Math.min(Math.max(newWidth, minWidth), maxWidth);
    }
    
    if (isVerticalResizing) {
      // Add class to body during resizing
      document.body.classList.add('resizing');
      
      // Calculate new console height based on mouse position
      const containerHeight = window.innerHeight;
      const mouseY = e.clientY;
      
      // Get the editor container to calculate relative position
      const editorContainer = document.querySelector('.flex.flex-col.flex-1.overflow-hidden');
      if (editorContainer) {
        const containerRect = editorContainer.getBoundingClientRect();
        const relativeY = mouseY - containerRect.top;
        const containerHeightPx = containerRect.height;
        
        // Calculate percentage (inverted since we're measuring from top but console is at bottom)
        let newConsoleHeightPercent = ((containerHeightPx - relativeY) / containerHeightPx) * 100;
        
        // Ensure console height is between 10% and 90%
        const minConsoleHeight = 10;
        const maxConsoleHeight = 90;
        consoleHeight = Math.min(Math.max(newConsoleHeightPercent, minConsoleHeight), maxConsoleHeight);
      }
    }
  }
  
  function handleMouseUp() {
    if (isResizing) {
      isResizing = false;
      // Remove resizing class
      document.body.classList.remove('resizing');
      // Save the width to localStorage
      localStorage.setItem('rightPanelWidth', rightPanelWidth.toString());
    }
    
    if (isVerticalResizing) {
      isVerticalResizing = false;
      // Remove resizing class
      document.body.classList.remove('resizing');
      // Save the console height to localStorage
      localStorage.setItem('consoleHeight', consoleHeight.toString());
    }
  }
  
  onMount(() => {
    // Load saved editor theme from localStorage
    const savedTheme = localStorage.getItem('editor-theme');
    if (savedTheme) {
      currentEditorTheme = savedTheme;
    }
    
    // Add global event listeners for resize operation
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    
    // Try to load saved width from localStorage
    const savedWidth = localStorage.getItem('rightPanelWidth');
    if (savedWidth) {
      rightPanelWidth = parseInt(savedWidth, 10);
    }
    
    // Try to load saved console height from localStorage
    const savedConsoleHeight = localStorage.getItem('consoleHeight');
    if (savedConsoleHeight) {
      consoleHeight = parseFloat(savedConsoleHeight);
    }
    
    // Initialize with a default startup file and a code buffer
    initializeEditorWithDefaultStartupFile();
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
    
    // Load documentation files if documentation tab is active
    if (activeTab === 'documentation') {
      loadDocumentationFiles();
    }
    
    // Load music example files if music examples tab is active
    if (activeTab === 'musicExamples') {
      loadMusicExampleFiles();
    }
    
    // Subscribe to appState changes to update UI
    const unsubscribe = appState.subscribe(state => {
      // Update console output (always update, even when empty)
      if (state.consoleOutput !== undefined) {
        // We're just using the store's version of the console output
        consoleOutput = state.consoleOutput;

        // Check if we should scroll (only when there's content)
        if (state.consoleOutput.length > 0) {
          scrollToBottom();
        }
      }
      
      // Check initialization status
      if (state.renardoInit) {
        initStatus = {
          superColliderClasses: state.renardoInit.superColliderClasses === true,
          sclangCode: state.renardoInit.sclangCode === true,
          samples: state.renardoInit.samples === true,
          instruments: state.renardoInit.instruments === true,
          reaperPack: state.renardoInit.reaperPack === true
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
    
    // Listen for code execution completion events
    const handleCodeExecutionComplete = (event) => {
      const { requestId } = event.detail;
      if (requestId) {
        removeExecutionHighlight(requestId);
      }
    };
    
    window.addEventListener('codeExecutionComplete', handleCodeExecutionComplete);
    
    // Clean up on unmount
    return () => {
      unsubscribe();
      document.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('codeExecutionComplete', handleCodeExecutionComplete);
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
  function sendCodeToExecute(codeToExecute, executionType = 'paragraph', from = null, to = null) {
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

    // Generate unique request ID
    const requestId = Date.now();

    // Highlight the executed code if range is provided
    if (from && to && editor) {
      highlightExecutedCode(from, to, requestId);
    }

    // Send to server with unique request ID to prevent duplicate execution
    sendMessage({
      type: 'execute_code',
      data: {
        code: codeToExecute,
        requestId: requestId
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
    let from, to;
    
    if (editor.somethingSelected()) {
      codeToExecute = editor.getSelection();
      executionType = 'selection';
      from = editor.getCursor('from');
      to = editor.getCursor('to');
    } else {
      codeToExecute = getCurrentParagraph();
      executionType = 'paragraph';
      // Calculate paragraph range
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
      
      from = { line: startLine, ch: 0 };
      to = { line: endLine, ch: editor.getLine(endLine).length };
    }
    
    sendCodeToExecute(codeToExecute, executionType, from, to);
  }
  
  // Execute current line - Mode 1: Alt+Enter
  function executeCurrentLine() {
    // Check if the editor is initialized
    if (!editor) {
      console.error("CodeMirror editor not initialized!");
      return;
    }
    
    const cursor = editor.getCursor();
    const currentLine = getCurrentLine();
    const from = { line: cursor.line, ch: 0 };
    const to = { line: cursor.line, ch: currentLine.length };
    
    sendCodeToExecute(currentLine, 'line', from, to);
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
  
  // Function to open new buffer modal
  function openNewBufferModal() {
    showNewBufferModal = true;
    newBufferName = '';
    
    // Focus the input field after the modal opens
    setTimeout(() => {
      const input = document.getElementById('new-buffer-name-input');
      if (input) input.focus();
    }, 100);
  }
  
  // Function to actually create the new buffer
  function createNewBuffer() {
    if (!newBufferName.trim()) return;
    
    const newBuffer = {
      id: nextTabId++,
      name: newBufferName.trim(),
      content: '',
      editing: false
    };
    tabs = [...tabs, newBuffer];
    activeTabId = newBuffer.id;
    
    showNewBufferModal = false;
    newBufferName = '';
    
    // Update editor if it exists
    if (editor) {
      editor.setValue(newBuffer.content);
      editor.setCursor({ line: 0, ch: 0 });
      editor.focus();
    }
  }
  
  // Function to cancel new buffer creation
  function cancelNewBuffer() {
    showNewBufferModal = false;
    newBufferName = '';
  }
  
  // Function to start editing a buffer name
  function startEditingBufferName(bufferId) {
    const buffer = tabs.find(t => t.id === bufferId);
    if (buffer) {
      buffer.editing = true;
      buffer.editingName = buffer.name;
      tabs = tabs; // Trigger reactivity
      
      // Focus the input after it's rendered
      setTimeout(() => {
        const input = document.getElementById(`buffer-name-input-${bufferId}`);
        if (input) {
          input.focus();
          input.select();
        }
      }, 10);
    }
  }
  
  // Function to finish editing a buffer name
  function finishEditingBufferName(bufferId) {
    const buffer = tabs.find(t => t.id === bufferId);
    if (buffer && buffer.editing) {
      if (buffer.editingName && buffer.editingName.trim()) {
        buffer.name = buffer.editingName.trim();
      }
      buffer.editing = false;
      tabs = tabs; // Trigger reactivity
    }
  }
  
  // Function to cancel editing a buffer name
  function cancelEditingBufferName(bufferId) {
    const buffer = tabs.find(t => t.id === bufferId);
    if (buffer && buffer.editing) {
      buffer.editing = false;
      delete buffer.editingName;
      tabs = tabs; // Trigger reactivity
    }
  }
  
  // Function to show close buffer confirmation
  function confirmCloseBuffer(bufferId) {
    bufferToClose = tabs.find(t => t.id === bufferId);
    showCloseBufferModal = true;
  }
  
  // Function to actually close a buffer
  function closeBuffer() {
    if (!bufferToClose || tabs.length <= 1) return;
    
    const bufferId = bufferToClose.id;
    tabs = tabs.filter(t => t.id !== bufferId);
    
    // If we closed the active buffer, switch to another one
    if (activeTabId === bufferId) {
      activeTabId = tabs[0].id;
    }
    
    // Reset modal state
    showCloseBufferModal = false;
    bufferToClose = null;
  }
  
  // Function to cancel closing a buffer
  function cancelCloseBuffer() {
    showCloseBufferModal = false;
    bufferToClose = null;
  }
  
  // Function to toggle zen mode
  function toggleZenMode() {
    zenMode = !zenMode;
    // Notify parent component
    const event = new CustomEvent('zenModeChange', { detail: { zenMode } });
    window.dispatchEvent(event);
  }
  
  // Function to toggle console minimize
  function toggleConsoleMinimize() {
    if (consoleMinimized) {
      // Expanding: restore previous height
      consoleHeight = consoleHeightBeforeMinimize;
      consoleMinimized = false;
    } else {
      // Minimizing: store current height and set to minimized height
      consoleHeightBeforeMinimize = consoleHeight;
      consoleHeight = minimizedConsoleHeight;
      consoleMinimized = true;
    }
  }
  
  // Function to highlight executed code
  function highlightExecutedCode(from, to, requestId) {
    if (!editor) return;
    
    const marker = editor.markText(from, to, {
      className: 'executed-code-highlight',
      clearOnEnter: false
    });
    
    activeHighlights.set(requestId, marker);
    
    // Remove highlight after animation completes (0.5 seconds)
    setTimeout(() => {
      if (activeHighlights.has(requestId)) {
        marker.clear();
        activeHighlights.delete(requestId);
      }
    }, 300);
  }
  
  // Function to remove highlight when response is received
  function removeExecutionHighlight(requestId) {
    if (activeHighlights.has(requestId)) {
      const marker = activeHighlights.get(requestId);
      marker.clear();
      activeHighlights.delete(requestId);
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
  async function loadTutorialFiles(lang = null) {
    loadingTutorials = true;
    try {
      const url = lang ? `/api/tutorial/files?lang=${lang}` : '/api/tutorial/files';
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        
        if (lang) {
          // Loading specific language
          tutorialFiles = data.files || [];
        } else {
          // Loading all languages - initialize available languages and default files
          availableLanguages = Object.keys(data.languages || {}).map(code => ({
            code,
            name: code === 'en' ? 'English' : code === 'es' ? 'Español' : code.toUpperCase()
          }));
          
          // Load files for the selected language
          if (data.languages && data.languages[selectedLanguage]) {
            tutorialFiles = data.languages[selectedLanguage];
          } else if (availableLanguages.length > 0) {
            // Fallback to first available language
            selectedLanguage = availableLanguages[0].code;
            tutorialFiles = data.languages[selectedLanguage] || [];
          }
        }
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
  
  // Function to handle language change
  async function changeLanguage(lang) {
    selectedLanguage = lang;
    await loadTutorialFiles(lang);
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
          content: content,
          editing: false
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
  // Make sure the current startup file tab is saved to disk  
  async function ensureStartupFileSaved() {
    if (!startupFileTab) return null;
    
    // If the startup file tab doesn't have a path, we need to save it
    if (!startupFileTab.startupFilePath) {
      try {
        // Create a new startup file
        const response = await fetch('/api/settings/user-directory/startup_files/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            filename: startupFileTab.name,
            content: startupFileTab.content
          })
        });
        
        const result = await response.json();
        if (result.success) {
          // Update the startup file tab with the path
          startupFileTab.startupFilePath = result.path;
          
          // Update tabs
          tabs = tabs.map(tab => 
            tab.id === startupFileTab.id ? {...tab, startupFilePath: result.path} : tab
          );
          
          // Reload startup files to get the new file in the list
          await loadStartupFiles();
          
          // Find the newly created file in the list
          const newFile = startupFiles.find(file => file.name === startupFileTab.name);
          if (newFile) {
            // Update the session startup file reference
            currentSession.startupFile = newFile;
            // Update selectedStartupFile
            selectedStartupFile = newFile;
            
            return newFile;
          }
        } else {
          console.error('Failed to save startup file:', result.message);
        }
      } catch (error) {
        console.error('Error saving startup file:', error);
      }
    } else {
      // The startup file already exists, just save it
      await saveStartupFile(startupFileTab);
      return currentSession.startupFile;
    }
    
    return null;
  }
  
  async function doSaveSession() {
    if (!sessionName.trim()) return;
    
    savingSession = true;
    try {
      // Ensure startup file is saved first if needed
      await ensureStartupFileSaved();
      
      // Start with startup file info section 
      let combinedContent = "";
      
      // Add startup file information - always include the startup file
      const startupSeparator = '//' + '='.repeat(78);
      
      if (currentSession.startupFile && startupFileTab) {
        // Use the session's startup file
        combinedContent += `${startupSeparator}\n`;
        combinedContent += `// STARTUP_FILE: ${currentSession.startupFile.name}\n`;
        combinedContent += `${startupSeparator}\n`;
        combinedContent += `${startupFileTab.content}\n\n`;
      } else if (startupFileTab) {
        // Use the current startup file tab even if not linked to the session
        combinedContent += `${startupSeparator}\n`;
        combinedContent += `// STARTUP_FILE: ${startupFileTab.name}\n`;
        combinedContent += `${startupSeparator}\n`;
        combinedContent += `${startupFileTab.content}\n\n`;
        
        // Update the session to link with this startup file
        // Find the corresponding file in the startupFiles list
        const startupFile = startupFiles.find(f => f.name === startupFileTab.name);
        if (startupFile) {
          currentSession.startupFile = startupFile;
        }
      }
      
      // Concatenate all non-startup buffers with separator and names
      const separator = '#'.repeat(80);
      const regularBuffers = tabs.filter(tab => !tab.isStartupFile);
      
      // Add regular buffers
      combinedContent += regularBuffers
        .map(tab => {
          const nameHeader = `######## ${tab.name}`;
          return `${separator}\n${nameHeader}\n${separator}\n${tab.content}`;
        })
        .join('\n');
      
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
        
        // Update session name
        currentSession.name = result.filename;
        currentSession.modified = false;
        
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
  
  // Function to open the sessions folder in the OS file browser
  async function openSessionsFolder() {
    try {
      const response = await fetch('/api/settings/user-directory/livecoding-sessions/open', {
        method: 'POST'
      });
      
      if (!response.ok) {
        const data = await response.json();
        console.error('Failed to open sessions folder:', data.message);
        addConsoleOutput(`Failed to open sessions folder: ${data.message}`, 'error');
      }
    } catch (error) {
      console.error('Error opening sessions folder:', error);
      addConsoleOutput(`Error opening sessions folder: ${error.message}`, 'error');
    }
  }
  
  // Startup files functions
  async function loadStartupFiles() {
    loadingStartupFiles = true;
    try {
      const response = await fetch('/api/settings/user-directory/startup_files');
      if (response.ok) {
        const data = await response.json();
        startupFiles = data.files || [];
        // Set default startup file
        if (startupFiles.length > 0 && !selectedStartupFile) {
          selectedStartupFile = startupFiles.find(file => file.name === 'startup.py') || startupFiles[0];
        }
      } else {
        console.error('Failed to load startup files');
        startupFiles = [];
      }
    } catch (error) {
      console.error('Error loading startup files:', error);
      startupFiles = [];
    } finally {
      loadingStartupFiles = false;
    }
  }
  
  // Initialize the editor with a default startup file and a code buffer
  async function initializeEditorWithDefaultStartupFile() {
    // Load the list of startup files
    await loadStartupFiles();
    
    // Find the default startup file (startup.py) or use the first one
    let defaultFile = startupFiles.find(file => file.name === 'startup.py');
    
    if (!defaultFile && startupFiles.length > 0) {
      defaultFile = startupFiles[0];
    }
    
    // If we found a default file, load it
    if (defaultFile) {
      // Load the startup file
      await loadStartupFile(defaultFile);
    } else {
      // Create a placeholder startup file tab if none exists
      const startupBuffer = {
        id: nextTabId++,
        name: 'startup.py',
        content: "# Renardo startup file\n# This file is loaded when Renardo starts\n# Add your custom code here\n",
        editing: false,
        isStartupFile: true,
        startupFilePath: null // Will be set when saved
      };
      
      // Add the startup file tab
      tabs = [startupBuffer];
    }
    
    // Add a default code buffer
    const codeBuffer = {
      id: nextTabId++,
      name: 'Untitled',
      content: ``,
      editing: false,
      isStartupFile: false
    };
    
    // Add the code buffer to the tabs
    tabs = [...tabs, codeBuffer];
    
    // Set the code buffer as active by default
    activeTabId = codeBuffer.id;
  }
  
  async function loadStartupFile(file) {
    try {
      // First, remove any existing startup file tab
      if (startupFileTab) {
        tabs = tabs.filter(tab => !tab.isStartupFile);
      }
      
      // Load the file from the server
      const response = await fetch(file.url);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Create a new buffer for the startup file - will always be at the beginning
          const newBuffer = {
            id: nextTabId++,
            name: file.name,
            content: data.content,
            editing: false,
            isStartupFile: true,
            startupFilePath: file.path
          };
          
          // Add the startup file as the first tab
          tabs = [newBuffer, ...tabs.filter(tab => !tab.isStartupFile)];
          activeTabId = newBuffer.id;
          
          if (editor) {
            editor.setValue(data.content);
            editor.setCursor({ line: 0, ch: 0 });
            editor.focus();
          }
          
          // Update selected startup file and session state
          selectedStartupFile = file;
          currentSession.startupFile = file;
          currentSession.modified = true;
        } else {
          console.error('Failed to load startup file:', data.message);
        }
      } else {
        console.error('Failed to load startup file');
      }
    } catch (error) {
      console.error('Error loading startup file:', error);
    }
  }
  
  async function saveStartupFile(buffer) {
    if (!buffer.isStartupFile || !buffer.startupFilePath) {
      console.error('Not a startup file');
      return;
    }
    
    try {
      // Get the latest content from the editor if this is the active buffer
      if (activeTabId === buffer.id && editor) {
        buffer.content = editor.getValue();
      }
      
      const response = await fetch('/api/settings/user-directory/startup_files/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          path: buffer.startupFilePath,
          content: buffer.content
        })
      });
      
      const result = await response.json();
      if (result.success) {
        // Update the buffer in the tabs array
        tabs = tabs.map(tab => 
          tab.id === buffer.id ? {...tab, content: buffer.content} : tab
        );
        
        // Show success message in console
        addConsoleOutput(`Startup file ${buffer.name} saved`, 'success');
      } else {
        alert(`Failed to save startup file: ${result.message}`);
      }
    } catch (error) {
      console.error('Error saving startup file:', error);
      alert('Error saving startup file');
    }
  }
  
  async function createNewStartupFile() {
    const fileName = prompt("Enter new startup file name:", "my_startup.py");
    if (!fileName) return;
    
    const name = fileName.endsWith('.py') ? fileName : `${fileName}.py`;
    
    // Check if a file with this name is already open
    const existingTabByName = tabs.find(
      tab => tab.isStartupFile && tab.name === name
    );
    
    if (existingTabByName) {
      // Just switch to the existing tab
      activeTabId = existingTabByName.id;
      if (editor) {
        editor.setValue(existingTabByName.content);
        editor.focus();
      }
      return;
    }
    
    try {
      const response = await fetch('/api/settings/user-directory/startup_files/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          filename: name,
          content: "# Renardo startup file\n# This file is loaded when Renardo starts if selected\n# Add your custom code here\n"
        })
      });
      
      const result = await response.json();
      if (result.success) {
        // Reload startup files
        await loadStartupFiles();
        // Load the newly created file
        const newFile = startupFiles.find(file => file.name === name);
        if (newFile) {
          loadStartupFile(newFile);
        }
      } else {
        alert(`Failed to create startup file: ${result.message}`);
      }
    } catch (error) {
      console.error('Error creating startup file:', error);
      alert('Error creating startup file');
    }
  }
  
  async function setDefaultStartupFile(file) {
    try {
      const response = await fetch('/api/settings/startup_files/set_default', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          filename: file.name
        })
      });
      
      const result = await response.json();
      if (result.success) {
        selectedStartupFile = file;
        addConsoleOutput(`Set ${file.name} as the default startup file`, 'success');
      } else {
        alert(`Failed to set default startup file: ${result.message}`);
      }
    } catch (error) {
      console.error('Error setting default startup file:', error);
      alert('Error setting default startup file');
    }
  }
  
  async function openStartupFilesFolder() {
    try {
      const response = await fetch('/api/settings/user-directory/startup_files/open', {
        method: 'POST'
      });
      
      if (!response.ok) {
        const data = await response.json();
        console.error('Failed to open startup files folder:', data.message);
        addConsoleOutput(`Failed to open startup files folder: ${data.message}`, 'error');
      }
    } catch (error) {
      console.error('Error opening startup files folder:', error);
      addConsoleOutput(`Error opening startup files folder: ${error.message}`, 'error');
    }
  }
  
  // Documentation functions
  async function loadDocumentationFiles() {
    loadingDocumentation = true;
    try {
      const response = await fetch('/api/documentation/files');
      if (response.ok) {
        const data = await response.json();
        documentationFiles = data.files || [];
        // Set default documentation file
        if (documentationFiles.length > 0 && !selectedDocumentationFile) {
          selectedDocumentationFile = documentationFiles.find(file => file.name === 'index.md') || documentationFiles[0];
          await loadDocumentationFile(selectedDocumentationFile);
        }
      } else {
        console.error('Failed to load documentation files');
        documentationFiles = [];
      }
    } catch (error) {
      console.error('Error loading documentation files:', error);
      documentationFiles = [];
    } finally {
      loadingDocumentation = false;
    }
  }
  
  // Music examples functions
  async function loadMusicExampleFiles() {
    loadingMusicExamples = true;
    try {
      const response = await fetch('/api/music-examples/files');
      if (response.ok) {
        const data = await response.json();
        musicExampleFiles = data.files || [];
      } else {
        console.error('Failed to load music example files');
        musicExampleFiles = [];
      }
    } catch (error) {
      console.error('Error loading music example files:', error);
      musicExampleFiles = [];
    } finally {
      loadingMusicExamples = false;
    }
  }
  
  // Function to load a music example file
  async function loadMusicExampleFile(file) {
    try {
      const response = await fetch(file.url);
      if (response.ok) {
        const content = await response.text();
        // Create a new buffer for the example
        const newBuffer = {
          id: nextTabId++,
          name: file.name.replace('.py', ''),
          content: content,
          editing: false
        };
        tabs = [...tabs, newBuffer];
        activeTabId = newBuffer.id;
        
        if (editor) {
          editor.setValue(content);
          editor.setCursor({ line: 0, ch: 0 });
          editor.focus();
        }
      } else {
        console.error('Failed to load music example file');
      }
    } catch (error) {
      console.error('Error loading music example file:', error);
    }
  }
  
  async function loadDocumentationFile(file) {
    try {
      const response = await fetch(file.url);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          currentDocumentationContent = data.content;
          selectedDocumentationFile = file;
        } else {
          console.error('Failed to load documentation file:', data.message);
          currentDocumentationContent = '# Error\n\nFailed to load documentation file.';
        }
      } else {
        console.error('Failed to load documentation file');
        currentDocumentationContent = '# Error\n\nFailed to load documentation file.';
      }
    } catch (error) {
      console.error('Error loading documentation file:', error);
      currentDocumentationContent = `# Error\n\nAn error occurred while loading the documentation: ${error.message}`;
    }
  }
  
  // Function to load a session file into the editor
  async function loadSessionFile(file) {
    try {
      const response = await fetch(file.url);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Reset session state
          currentSession = {
            name: file.name,
            startupFile: null,
            modified: false
          };
          
          // First check for a startup file section
          const startupFileMatch = data.content.match(/\/\/={78}\n\/\/ STARTUP_FILE: (.+?)\n\/\/={78}\n([\s\S]+?)\n\n/);
          
          let startupFileName = null;
          let startupFileContent = null;
          let remainingContent = data.content;
          
          if (startupFileMatch) {
            startupFileName = startupFileMatch[1];
            startupFileContent = startupFileMatch[2];
            
            // Remove the startup section from the content for regular buffer processing
            remainingContent = data.content.substring(startupFileMatch[0].length);
          }
          
          // Parse content with buffer names
          const separator = '#'.repeat(80);
          const parts = remainingContent.split(new RegExp(`\\n?${separator}\\n?`));
          
          // Clear existing tabs and create new ones from the loaded content
          tabs = [];
          let newTabId = 1;
          
          // Add regular buffers
          for (let i = 0; i < parts.length; i++) {
            const part = parts[i].trim();
            if (!part) continue;
            
            // Check if this part contains a buffer name header
            if (part.startsWith('######## ')) {
              const nameHeaderMatch = part.match(/^######## (.+?)(?:\n|$)/);
              if (nameHeaderMatch && i + 1 < parts.length) {
                const bufferName = nameHeaderMatch[1];
                const bufferContent = parts[i + 1].trim();
                
                tabs.push({
                  id: newTabId++,
                  name: bufferName,
                  content: bufferContent,
                  editing: false,
                  isStartupFile: false
                });
                
                i++; // Skip the content part we just processed
              }
            } else {
              // Legacy format without names
              tabs.push({
                id: newTabId++,
                name: `Untitled ${tabs.length + 1}`,
                content: part,
                editing: false,
                isStartupFile: false
              });
            }
          }
          
          // If we found a startup file, we need to load it
          if (startupFileName && startupFileContent) {
            // Try to find the actual file in the startup files list
            await loadStartupFiles(); // Make sure we have the latest list
            
            const startupFile = startupFiles.find(f => f.name === startupFileName);
            
            if (startupFile) {
              // Load the real file from the server but use our content
              currentSession.startupFile = startupFile;
              
              // Create the startup file tab (always first)
              const startupTab = {
                id: newTabId++,
                name: startupFileName,
                content: startupFileContent,
                editing: false,
                isStartupFile: true,
                startupFilePath: startupFile.path
              };
              
              // Add to beginning of tabs
              tabs = [startupTab, ...tabs];
              
              // Update selected startup file
              selectedStartupFile = startupFile;
            } else {
              // The startup file wasn't found in the system, create a local tab only
              console.warn(`Startup file ${startupFileName} not found in the system`);
              
              // Create a local buffer for the startup file content
              const localStartupTab = {
                id: newTabId++,
                name: startupFileName,
                content: startupFileContent,
                editing: false,
                isStartupFile: true,
                startupFilePath: null // No path since we don't have the real file
              };
              
              // Add to beginning of tabs
              tabs = [localStartupTab, ...tabs];
            }
          }
          
          // If no buffers were created, create at least one
          if (tabs.length === 0) {
            tabs.push({
              id: newTabId,
              name: 'Untitled',
              content: '',
              editing: false,
              isStartupFile: false
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
          
          // Show success message
          addConsoleOutput(`Session "${file.name}" loaded successfully`, 'success');
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

<div class="flex flex-col w-full overflow-hidden" style="height: {zenMode ? '100vh' : 'calc(100vh - 4rem)'}">
  <!-- Zen mode toggle button -->
  <div class="absolute top-2 right-2 z-50">
    <button
      class="btn btn-sm btn-ghost"
      on:click={toggleZenMode}
      title="{zenMode ? 'Exit' : 'Enter'} Zen Mode"
    >
      {#if zenMode}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
        </svg>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
          <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
        </svg>
      {/if}
    </button>
  </div>

  <!-- Console minimize toggle button -->
  <div class="absolute bottom-2 left-2 z-50">
    <button
      class="btn btn-sm btn-ghost"
      on:click={toggleConsoleMinimize}
      title="{consoleMinimized ? 'Expand' : 'Minimize'} Console"
    >
      {#if consoleMinimized}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
        </svg>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      {/if}
    </button>
  </div>
  
  <!-- Header with controls -->
  {#if !zenMode}
    <div class="bg-base-300 p-4" transition:slide>
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
            on:click={() => {
              const allText = editor.getValue();
              const from = { line: 0, ch: 0 };
              const to = { line: editor.lineCount() - 1, ch: editor.getLine(editor.lineCount() - 1).length };
              sendCodeToExecute(allText, 'all', from, to);
            }}
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
          
          {#if activeBuffer && activeBuffer.isStartupFile}
            <button
              class="btn btn-sm btn-info"
              on:click={() => saveStartupFile(activeBuffer)}
              title="Save current startup file"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 012 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
              Save Startup File
            </button>
          {/if}
        </div>

        <!-- Editor Theme Selector -->
        <div class="flex items-center gap-2">
          <CodeMirrorThemeSelector 
            bind:editor={editor} 
            on:themeChange={event => currentEditorTheme = event.detail.theme}
          />
        </div>
      </div>
    </div>
  </div>
  {/if}

  <!-- Buffer tabs -->
  <div class="bg-base-200 px-4 py-0.5">
    <div class="flex items-center justify-between gap-1 h-8">
      <div class="flex items-center gap-1">
      {#each tabs as buffer}
        <button
          class="tab tab-lifted {activeTabId === buffer.id ? 'tab-active' : ''} {buffer.isStartupFile ? 'startup-file' : ''}"
          on:click={() => activeTabId = buffer.id}
          on:dblclick={() => startEditingBufferName(buffer.id)}
          title={buffer.isStartupFile ? 'Startup File - Will run when Renardo starts' : buffer.name}
        >
          {#if buffer.editing}
            <input
              id="buffer-name-input-{buffer.id}"
              type="text"
              class="bg-transparent outline-none w-24"
              bind:value={buffer.editingName}
              on:keydown={(e) => {
                if (e.key === 'Enter') {
                  finishEditingBufferName(buffer.id);
                } else if (e.key === 'Escape') {
                  cancelEditingBufferName(buffer.id);
                }
              }}
              on:blur={() => finishEditingBufferName(buffer.id)}
              on:click|stopPropagation
            />
          {:else}
            {#if buffer.isStartupFile}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 inline-block" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
              </svg>
            {/if}
            {buffer.name}
          {/if}
          {#if !buffer.isStartupFile && tabs.length > 1}
            <button
              class="ml-2 w-4 h-4 rounded-full hover:bg-base-300 flex items-center justify-center text-xs"
              on:click|stopPropagation={() => confirmCloseBuffer(buffer.id)}
            >
              ×
            </button>
          {/if}
        </button>
      {/each}
      <button
        class="tab tab-lifted"
        on:click={openNewBufferModal}
        title="New Buffer"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
    
    <!-- Right Panel Toggle -->
    <button
      class="btn btn-sm btn-outline"
      on:click={() => {
        rightPanelOpen = !rightPanelOpen;
        if (!rightPanelOpen) return;
        // Reload files when opening the panel
        if (activeTab === 'tutorial') {
          if (availableLanguages.length === 0) {
            loadTutorialFiles(); // Load all languages first
          } else {
            loadTutorialFiles(selectedLanguage); // Load current language
          }
        } else if (activeTab === 'sessions') {
          loadSessionFiles();
        } else if (activeTab === 'startupFiles') {
          loadStartupFiles();
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
    </div>
  </div>

  <!-- Main workspace -->
  <div class="flex flex-1 overflow-hidden">
    <!-- Left side: Code editor and console -->
    <div class="flex flex-col flex-1 overflow-hidden">
      <!-- Code editor -->
      <div class="flex-none border border-base-300 overflow-hidden" 
           style="height: {100 - consoleHeight}%" 
           bind:this={editorContainer}>
        <textarea id="code-editor">{editorContent}</textarea>
      </div>

      <!-- Vertical resizable divider -->
      <div 
        class="h-1 hover:h-1 cursor-row-resize flex-shrink-0 bg-base-300 hover:bg-primary hover:opacity-50 transition-colors" 
        on:mousedown={(e) => {
          isVerticalResizing = true;
          e.preventDefault();
        }}
      ></div>

      <!-- Console output - always below editor -->
      <div class="flex flex-col flex-none console-background overflow-hidden"
           style="height: {consoleHeight}%; background-color: {consoleColors.consoleBg}; color: {consoleColors.textColor};">
        {#if !consoleMinimized}
        <div class="flex justify-between items-center px-4 py-2 console-header"
             style="background-color: {consoleColors.consoleHeaderBg}; color: {consoleColors.textColor};">
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
        {/if}
        <div class="overflow-y-auto flex-1 p-4 font-mono text-sm" bind:this={consoleContainer}>
          {#if consoleOutput.length === 0}
            <div class="flex items-center justify-center h-full opacity-50 italic">
              {consoleMinimized ? '' : 'No output yet. Run some code to see results here.'}
            </div>
          {:else}
            {#each (consoleMinimized ? consoleOutput.slice(-2) : consoleOutput) as output}
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

    <!-- Resizable divider -->
    {#if rightPanelOpen}
      <div 
        class="w-1 hover:w-1 cursor-col-resize flex-shrink-0 bg-base-300 hover:bg-primary hover:opacity-50 transition-colors" 
        on:mousedown={(e) => {
          isResizing = true;
          e.preventDefault();
        }}
      ></div>
    {/if}
    
    <!-- Right side: Collapsible panel with tabs -->
    {#if rightPanelOpen}
      <div transition:fade={{ duration: 200 }} 
        class="flex flex-col border-l border-base-300 bg-base-100 transition-all" 
        style="width: {rightPanelWidth}px;">
        <!-- Panel header with tabs and close button -->
        <div class="bg-base-300 p-2">
          <div class="flex justify-between items-center mb-2">
            <div class="tabs tabs-boxed">
              <button 
                class="tab {activeTab === 'tutorial' ? 'tab-active' : ''}" 
                on:click={() => {
                  activeTab = 'tutorial';
                  if (availableLanguages.length === 0) {
                    loadTutorialFiles(); // Load all languages first
                  }
                }}>
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
                class="tab {activeTab === 'startupFiles' ? 'tab-active' : ''}" 
                on:click={() => {activeTab = 'startupFiles'; loadStartupFiles();}}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Startup Files
              </button>
              <button 
                class="tab {activeTab === 'musicExamples' ? 'tab-active' : ''}" 
                on:click={() => {activeTab = 'musicExamples'; loadMusicExampleFiles();}}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
                </svg>
                Music Examples
              </button>
              <button 
                class="tab {activeTab === 'documentation' ? 'tab-active' : ''}" 
                on:click={() => {activeTab = 'documentation'; loadDocumentationFiles();}}>
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
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-bold">Tutorials</h3>
                {#if availableLanguages.length > 1}
                  <select 
                    class="select select-sm select-bordered w-24"
                    bind:value={selectedLanguage}
                    on:change={(e) => changeLanguage(e.target.value)}
                  >
                    {#each availableLanguages as lang}
                      <option value={lang.code}>{lang.name}</option>
                    {/each}
                  </select>
                {/if}
              </div>
              {#if loadingTutorials}
                <div class="flex justify-center">
                  <span class="loading loading-spinner loading-md"></span>
                </div>
              {:else if tutorialFiles.length === 0}
                <p class="text-sm opacity-70">No tutorial files available for this language.</p>
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
          {:else if activeTab === 'startupFiles'}
            <div>
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-bold">Startup Files</h3>
                <div class="flex gap-2">
                  <button
                    class="btn btn-sm btn-outline"
                    on:click={createNewStartupFile}
                    title="Create New Startup File"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                    </svg>
                    New
                  </button>
                  <button
                    class="btn btn-sm btn-outline"
                    on:click={openStartupFilesFolder}
                    title="Open Startup Files Folder"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H8a3 3 0 00-3 3v1.5a1.5 1.5 0 01-3 0V6z" clip-rule="evenodd" />
                      <path d="M6 12a2 2 0 012-2h8a2 2 0 012 2v2a2 2 0 01-2 2H2h2a2 2 0 002-2v-2z" />
                    </svg>
                    Open Folder
                  </button>
                </div>
              </div>
              <p class="text-sm mb-4">
                Startup files contain code that runs when Renardo starts. Select a default startup file below:
              </p>
              {#if loadingStartupFiles}
                <div class="flex justify-center">
                  <span class="loading loading-spinner loading-md"></span>
                </div>
              {:else if startupFiles.length === 0}
                <div class="alert alert-info">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  <span>No startup files found. Click "New" to create one.</span>
                </div>
              {:else}
                <div class="space-y-2">
                  {#each startupFiles as file}
                    <div class="flex items-center gap-2">
                      <button
                        class="flex-grow text-left btn btn-sm btn-outline justify-start 
                               {selectedStartupFile && selectedStartupFile.name === file.name ? 'btn-primary' : ''}"
                        on:click={() => loadStartupFile(file)}
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clip-rule="evenodd" />
                        </svg>
                        {file.name}
                      </button>
                      <div class="flex gap-1">
                        {#if currentSession.startupFile && currentSession.startupFile.name === file.name}
                          <div class="badge badge-accent">Session</div>
                        {/if}
                        {#if selectedStartupFile && selectedStartupFile.name === file.name}
                          <div class="badge badge-primary">Default</div>
                        {:else}
                          <button
                            class="btn btn-xs btn-outline"
                            on:click={() => setDefaultStartupFile(file)}
                            title="Set as Default Startup File"
                          >
                            Set Default
                          </button>
                        {/if}
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          {:else if activeTab === 'musicExamples'}
            <div>
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-bold">Music Examples</h3>
              </div>
              
              {#if loadingMusicExamples}
                <div class="flex justify-center items-center p-8">
                  <div class="loading loading-spinner loading-md"></div>
                </div>
              {:else if musicExampleFiles.length === 0}
                <div class="flex flex-col justify-center items-center p-8">
                  <p class="text-sm opacity-70 mb-4">No music examples found.</p>
                  <button 
                    class="btn btn-sm btn-primary" 
                    on:click={loadMusicExampleFiles}
                  >
                    Reload
                  </button>
                </div>
              {:else}
                <div class="examples-list space-y-1 px-1">
                  {#each musicExampleFiles as file}
                    <button
                      class="w-full text-left px-3 py-2 rounded hover:bg-base-200 transition-colors"
                      on:click={() => loadMusicExampleFile(file)}
                    >
                      <div class="flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 text-primary" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
                        </svg>
                        <span class="text-sm font-medium">{file.name.replace('.py', '')}</span>
                      </div>
                      {#if file.description}
                        <p class="text-xs opacity-70 ml-6 mt-1">{file.description}</p>
                      {/if}
                    </button>
                  {/each}
                </div>
              {/if}
            </div>
          {:else if activeTab === 'sessions'}
            <div>
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-bold">Sessions</h3>
                <button
                  class="btn btn-sm btn-outline"
                  on:click={openSessionsFolder}
                  title="Open Sessions Folder in File Explorer"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H8a3 3 0 00-3 3v1.5a1.5 1.5 0 01-3 0V6z" clip-rule="evenodd" />
                    <path d="M6 12a2 2 0 012-2h8a2 2 0 012 2v2a2 2 0 01-2 2H2h2a2 2 0 002-2v-2z" />
                  </svg>
                  Open Folder
                </button>
              </div>
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
            <div class="h-full flex flex-col">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-bold">Renardo Documentation</h3>
                <div class="flex gap-2">
                  {#if documentationFiles.length > 0}
                    <button
                      class="btn btn-sm btn-outline"
                      on:click={() => loadDocumentationFile(documentationFiles.find(file => file.name === 'index.md') || documentationFiles[0])}
                      title="Go to Documentation Home"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                      </svg>
                    </button>
                  {/if}
                </div>
              </div>
              
              <div class="doc-container flex flex-1 overflow-hidden">
                {#if loadingDocumentation}
                  <div class="w-full flex justify-center items-center">
                    <div class="loading loading-spinner loading-md"></div>
                  </div>
                {:else if documentationFiles.length === 0}
                  <div class="w-full flex flex-col justify-center items-center">
                    <p class="text-sm opacity-70 mb-4">No documentation files found.</p>
                    <button 
                      class="btn btn-sm btn-primary" 
                      on:click={loadDocumentationFiles}
                    >
                      Load Documentation
                    </button>
                  </div>
                {:else}
                  <!-- Documentation sidebar -->
                  <div class="doc-sidebar w-1/4 pr-4 border-r border-base-300 overflow-y-auto">
                    <ul class="menu menu-sm p-0">
                      {#each documentationFiles as file}
                        <li>
                          <button 
                            class="text-sm py-1 px-2 {selectedDocumentationFile && selectedDocumentationFile.path === file.path ? 'bg-primary/10 font-medium' : ''}"
                            on:click={() => loadDocumentationFile(file)}
                          >
                            {file.title || file.name.replace('.md', '')}
                          </button>
                        </li>
                      {/each}
                    </ul>
                  </div>
                  
                  <!-- Documentation content -->
                  <div class="doc-content w-3/4 pl-4 overflow-y-auto">
                    {#if currentDocumentationContent}
                      <div class="prose prose-sm max-w-none dark:prose-invert">
                        {@html currentDocumentationContent}
                      </div>
                    {:else}
                      <div class="flex justify-center items-center h-full">
                        <p class="text-sm opacity-70">Select a documentation file to view its contents.</p>
                      </div>
                    {/if}
                  </div>
                {/if}
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
          
          <div class="flex items-center">
            <div class="w-6 h-6 mr-2">
              {#if initStatus.reaperPack}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {/if}
            </div>
            <span class="{initStatus.reaperPack ? 'text-success' : 'text-error'}">Reaper Resources</span>
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

<!-- New Buffer Modal -->
{#if showNewBufferModal}
  <div class="modal modal-open" transition:fade={{ duration: 200 }}>
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">New Buffer</h3>
      
      <div class="form-control">
        <label for="new-buffer-name-input" class="label">
          <span class="label-text">Buffer Name</span>
        </label>
        <input 
          id="new-buffer-name-input"
          type="text" 
          placeholder="Enter buffer name" 
          class="input input-bordered w-full"
          bind:value={newBufferName}
          on:keydown={(e) => {
            if (e.key === 'Enter' && newBufferName.trim()) {
              createNewBuffer();
            } else if (e.key === 'Escape') {
              cancelNewBuffer();
            }
          }}
          disabled={creatingBuffer}
        />
      </div>
      
      <div class="modal-action">
        <button 
          class="btn btn-primary"
          on:click={createNewBuffer}
          disabled={!newBufferName.trim() || creatingBuffer}
        >
          Create
        </button>
        <button 
          class="btn btn-outline"
          on:click={cancelNewBuffer}
          disabled={creatingBuffer}
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Close Buffer Confirmation Modal -->
{#if showCloseBufferModal && bufferToClose}
  <div class="modal modal-open" transition:fade={{ duration: 200 }}>
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">Close Buffer</h3>
      
      <p class="mb-4">
        Are you sure you want to close the buffer "{bufferToClose.name}"?
      </p>
      
      <div class="alert alert-warning mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
        <span>Any unsaved changes will be lost.</span>
      </div>
      
      <div class="modal-action">
        <button 
          class="btn btn-error"
          on:click={closeBuffer}
        >
          Close Buffer
        </button>
        <button 
          class="btn btn-outline"
          on:click={cancelCloseBuffer}
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
    padding: 0.125rem 0.75rem;
    margin-right: 0.25rem;
    font-size: 0.8rem;
    height: 2rem;
    display: flex;
    align-items: center;
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
  
  /* Ensure the editor container has proper height constraints */
  :global(.CodeMirror-scroll) {
    max-height: 100%;
    overflow-y: auto !important;
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
  
  /* Disable text selection during resize */
  :global(body.resizing) {
    user-select: none;
    cursor: col-resize;
  }
  
  /* Startup file tab styling */
  .startup-file {
    background-color: oklch(var(--p) / 0.2); /* Primary color with some transparency */
    border-bottom: 2px solid oklch(var(--p)); /* Primary color border bottom */
    font-weight: bold;
  }
  
  .startup-file.tab-active {
    background-color: oklch(var(--p) / 0.3); /* Slightly darker when active */
  }
  
  /* Console styling */
  .console-background {
    /* These will be overridden by inline styles */
    background-color: #21222c; /* Default - matches Dracula darker */
    color: #f8f8f2; /* Light text for dark backgrounds */
  }
  
  .console-header {
    /* These will be overridden by inline styles */
    background-color: #191a21; /* Default - matches Dracula darkest */
    color: #f8f8f2; /* Light text for dark backgrounds */
  }
  
  /* Executed code highlighting */
  :global(.executed-code-highlight) {
    background-color: rgba(0, 255, 255, 0.3); /* Cyan color with transparency - should work across themes */
    animation: highlight-blink 0.5s ease-in-out;
  }
  
  @keyframes highlight-blink {
    0% { background-color: rgba(0, 255, 255, 0.6); }
    50% { background-color: rgba(0, 255, 255, 0.2); }
    100% { background-color: transparent; }
  }
  /* Documentation styles */
  .doc-container {
    height: calc(100% - 3rem);
  }
  
  .doc-sidebar, .doc-content {
    height: 100%;
    overflow-y: auto;
  }
  
  .doc-content :global(pre) {
    background-color: rgba(0, 0, 0, 0.1);
    padding: 1rem;
    border-radius: 0.25rem;
    overflow-x: auto;
  }
  
  .doc-content :global(code) {
    background-color: rgba(0, 0, 0, 0.1);
    padding: 0.125rem 0.25rem;
    border-radius: 0.125rem;
    font-family: monospace;
  }
  
  .doc-content :global(h1) {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }
  
  .doc-content :global(h2) {
    font-size: 1.25rem;
    font-weight: 600;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
  }
  
  .doc-content :global(h3) {
    font-size: 1.125rem;
    font-weight: 600;
    margin-top: 1.25rem;
    margin-bottom: 0.5rem;
  }
  
  .doc-content :global(p) {
    margin-bottom: 1rem;
  }
  
  .doc-content :global(ul), .doc-content :global(ol) {
    margin-bottom: 1rem;
    padding-left: 1.5rem;
  }
  
  .doc-content :global(li) {
    margin-bottom: 0.25rem;
  }
</style>
