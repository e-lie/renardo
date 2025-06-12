<script>
  import { onMount, onDestroy } from 'svelte';
  import { slide } from 'svelte/transition';
  import { appState } from './lib/appState.js';
  import { sendMessage } from './lib/websocket.js';
  
  // Import components
  import EditorTabs from './components/editor/EditorTabs.svelte';
  import CodeMirrorEditor from './components/editor/CodeMirrorEditor.svelte';
  import ConsoleOutput from './components/editor/ConsoleOutput.svelte';
  import RightPanel from './components/editor/RightPanel.svelte';
  import InitializationModal from './components/modals/InitializationModal.svelte';
  import SaveSessionModal from './components/modals/SaveSessionModal.svelte';
  import NewBufferModal from './components/modals/NewBufferModal.svelte';
  import CloseBufferModal from './components/modals/CloseBufferModal.svelte';
  import CodeMirrorThemeSelector from './lib/CodeMirrorThemeSelector.svelte';
  
  // State for right panel
  let rightPanelOpen = true;
  let rightPanelWidth = 384;
  let activeRightTab = 'tutorial';
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
  let consoleHeight = 30;
  let isVerticalResizing = false;
  let consoleMinimized = false;
  
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
  
  // Modal states
  let showSaveModal = false;
  let savingSession = false;
  let showNewBufferModal = false;
  let showCloseBufferModal = false;
  let bufferToClose = null;
  let showInitModal = false;
  let initStatus = {
    superColliderClasses: false,
    sclangCode: false,
    samples: false,
    instruments: false,
    reaperPack: false
  };
  let modalDismissed = false;
  
  // Zen mode state
  let zenMode = false;
  
  // Code execution highlighting state
  let activeHighlights = new Map();
  
  // Session state
  let currentSession = {
    name: 'Untitled Session',
    startupFile: null,
    modified: false
  };
  
  // State for multi-tab editor
  let tabs = [];
  let activeTabId = 1;
  let nextTabId = 2;
  
  // Editor component and CodeMirror instance references
  let editorComponent;
  let themeSelector;
  let currentEditorTheme = "dracula";
  
  // Console output
  let consoleOutput = [];
  
  // Get the active tab's content
  $: activeBuffer = tabs.find(t => t.id === activeTabId);
  $: editorContent = activeBuffer ? activeBuffer.content : '';
  $: startupFileTab = tabs.find(tab => tab.isStartupFile);
  
  // Runtime status
  let scBackendRunning = false;
  let renardoRuntimeRunning = false;
  
  // Resize handlers
  function handleMouseMove(e) {
    if (isResizing) {
      document.body.classList.add('resizing');
      const containerWidth = document.body.clientWidth;
      const mouseX = e.clientX;
      const minWidth = 240;
      const maxWidth = containerWidth * 0.5;
      const newWidth = containerWidth - mouseX;
      rightPanelWidth = Math.min(Math.max(newWidth, minWidth), maxWidth);
    }
    
    if (isVerticalResizing) {
      document.body.classList.add('resizing');
      const containerHeight = window.innerHeight;
      const mouseY = e.clientY;
      const editorContainer = document.querySelector('.flex.flex-col.flex-1.overflow-hidden');
      if (editorContainer) {
        const containerRect = editorContainer.getBoundingClientRect();
        const relativeY = mouseY - containerRect.top;
        const containerHeightPx = containerRect.height;
        let newConsoleHeightPercent = ((containerHeightPx - relativeY) / containerHeightPx) * 100;
        const minConsoleHeight = 10;
        const maxConsoleHeight = 90;
        consoleHeight = Math.min(Math.max(newConsoleHeightPercent, minConsoleHeight), maxConsoleHeight);
      }
    }
  }
  
  function handleMouseUp() {
    if (isResizing) {
      isResizing = false;
      document.body.classList.remove('resizing');
      localStorage.setItem('rightPanelWidth', rightPanelWidth.toString());
    }
    
    if (isVerticalResizing) {
      isVerticalResizing = false;
      document.body.classList.remove('resizing');
      localStorage.setItem('consoleHeight', consoleHeight.toString());
    }
  }
  
  // Editor event handlers
  function handleEditorReady(event) {
    // The editor component is already stored in editorComponent via bind:this
    // Initialize theme selector with the raw CodeMirror instance
    if (themeSelector) {
      themeSelector.initEditor(event.detail.editor);
    }
  }
  
  function handleEditorChange(event) {
    const currentBuffer = tabs.find(t => t.id === activeTabId);
    if (currentBuffer) {
      currentBuffer.content = event.detail.value;
      tabs = tabs;
    }
  }
  
  function handleEditorExecute(event) {
    const mode = event.detail.mode;
    if (mode === 'line') {
      executeCurrentLine();
    } else {
      executeCode();
    }
  }
  
  // Tab management handlers
  function handleSwitchTab(event) {
    activeTabId = event.detail.tabId;
    if (editorComponent) {
      editorComponent.setValue(tabs.find(t => t.id === activeTabId).content);
      editorComponent.focus();
    }
  }
  
  function handleStartEditingName(event) {
    const buffer = tabs.find(t => t.id === event.detail.bufferId);
    if (buffer) {
      buffer.editing = true;
      buffer.editingName = buffer.name;
      tabs = tabs;
    }
  }
  
  function handleFinishEditingName(event) {
    const buffer = tabs.find(t => t.id === event.detail.bufferId);
    if (buffer && buffer.editing) {
      if (event.detail.newName && event.detail.newName.trim()) {
        buffer.name = event.detail.newName.trim();
      }
      buffer.editing = false;
      tabs = tabs;
    }
  }
  
  function handleCancelEditingName(event) {
    const buffer = tabs.find(t => t.id === event.detail.bufferId);
    if (buffer && buffer.editing) {
      buffer.editing = false;
      delete buffer.editingName;
      tabs = tabs;
    }
  }
  
  function handleCloseBuffer(event) {
    bufferToClose = tabs.find(t => t.id === event.detail.bufferId);
    showCloseBufferModal = true;
  }
  
  function handleNewBuffer() {
    showNewBufferModal = true;
  }
  
  function handleSaveStartupFile(event) {
    saveStartupFile(event.detail.buffer);
  }
  
  // Right panel handlers
  function handleRightPanelSwitchTab(event) {
    activeRightTab = event.detail.tab;
    
    // Load data when switching tabs
    switch (activeRightTab) {
      case 'tutorial':
        if (availableLanguages.length === 0) {
          loadTutorialFiles();
        }
        break;
      case 'sessions':
        loadSessionFiles();
        break;
      case 'startupFiles':
        loadStartupFiles();
        break;
      case 'musicExamples':
        loadMusicExampleFiles();
        break;
      case 'documentation':
        loadDocumentationFiles();
        break;
    }
  }
  
  // Console handlers
  function handleConsoleToggleMinimize(event) {
    consoleMinimized = event.detail.minimized;
    consoleHeight = event.detail.height;
  }
  
  function handleConsoleClear() {
    appState.update(state => ({
      ...state,
      consoleOutput: []
    }));
  }
  
  // Modal handlers
  function handleInitModalDismiss() {
    showInitModal = false;
    modalDismissed = true;
    
    const missingSteps = [];
    if (!initStatus.superColliderClasses) missingSteps.push("SuperCollider Classes");
    if (!initStatus.sclangCode) missingSteps.push("SCLang Code");
    if (!initStatus.samples) missingSteps.push("Sample Packs");
    if (!initStatus.instruments) missingSteps.push("Instruments & Effects");
    
    if (missingSteps.length > 0) {
      addConsoleOutput(
        `⚠️ Warning: Some initialization steps are incomplete (${missingSteps.join(", ")}). Some features may not work properly.`,
        'warn'
      );
    }
  }
  
  function handleInitModalGoToInit() {
    window.location.hash = 'init';
  }
  
  function handleSaveSession(event) {
    doSaveSession(event.detail.name);
  }
  
  function handleCreateNewBuffer(event) {
    const newBuffer = {
      id: nextTabId++,
      name: event.detail.name,
      content: '',
      editing: false
    };
    tabs = [...tabs, newBuffer];
    activeTabId = newBuffer.id;
    
    showNewBufferModal = false;
    
    if (editorComponent) {
      editorComponent.setValue(newBuffer.content);
      editorComponent.setCursor({ line: 0, ch: 0 });
      editorComponent.focus();
    }
  }
  
  function closeBuffer() {
    if (!bufferToClose || tabs.length <= 1) return;
    
    const bufferId = bufferToClose.id;
    tabs = tabs.filter(t => t.id !== bufferId);
    
    if (activeTabId === bufferId) {
      activeTabId = tabs[0].id;
    }
    
    showCloseBufferModal = false;
    bufferToClose = null;
  }
  
  // Browser/viewer handlers
  function handleTutorialChangeLanguage(event) {
    changeLanguage(event.detail.language);
  }
  
  function handleTutorialLoadFile(event) {
    loadTutorialFile(event.detail.file);
  }
  
  function handleSessionLoadFile(event) {
    loadSessionFile(event.detail.file);
  }
  
  function handleSessionOpenFolder() {
    openSessionsFolder();
  }
  
  function handleStartupLoadFile(event) {
    loadStartupFile(event.detail.file);
  }
  
  function handleStartupCreateNew() {
    createNewStartupFile();
  }
  
  function handleStartupOpenFolder() {
    openStartupFilesFolder();
  }
  
  function handleStartupSetDefault(event) {
    setDefaultStartupFile(event.detail.file);
  }
  
  function handleMusicExampleLoadFile(event) {
    loadMusicExampleFile(event.detail.file);
  }
  
  function handleMusicExampleReload() {
    loadMusicExampleFiles();
  }
  
  function handleDocumentationLoadFile(event) {
    loadDocumentationFile(event.detail.file);
  }
  
  function handleDocumentationGoHome() {
    loadDocumentationFile(documentationFiles.find(file => file.name === 'index.md') || documentationFiles[0]);
  }
  
  // Send code to server
  function sendCodeToExecute(codeToExecute, executionType = 'paragraph', from = null, to = null) {
    if (!codeToExecute || !codeToExecute.trim()) {
      return;
    }

    const requestId = Date.now();

    if (from && to && editorComponent) {
      editorComponent.highlightExecutedCode(from, to, requestId);
    }

    sendMessage({
      type: 'execute_code',
      data: {
        code: codeToExecute,
        requestId: requestId
      }
    });
  }
  
  // Execute code
  function executeCode() {
    if (!editorComponent) {
      console.error("CodeMirror editor not initialized!");
      return;
    }
    
    let codeToExecute;
    let executionType;
    let from, to;
    
    const selection = editorComponent.getSelection();
    if (selection) {
      codeToExecute = selection.text;
      executionType = 'selection';
      from = selection.from;
      to = selection.to;
    } else {
      const paragraph = editorComponent.getCurrentParagraph();
      codeToExecute = paragraph.text;
      executionType = 'paragraph';
      from = paragraph.from;
      to = paragraph.to;
    }
    
    sendCodeToExecute(codeToExecute, executionType, from, to);
  }
  
  // Execute current line
  function executeCurrentLine() {
    if (!editorComponent) {
      console.error("CodeMirror editor not initialized!");
      return;
    }
    
    const line = editorComponent.getCurrentLine();
    sendCodeToExecute(line.text, 'line', line.from, line.to);
  }
  
  // Stop music
  function stopMusic() {
    sendMessage({
      type: 'execute_code',
      data: {
        code: 'Clock.clear()',
        requestId: Date.now()
      }
    });
  }
  
  // Save session
  function saveSession() {
    showSaveModal = true;
  }
  
  // Load session
  function loadSession() {
    rightPanelOpen = true;
    activeRightTab = 'sessions';
    loadSessionFiles();
  }
  
  // Toggle zen mode
  function toggleZenMode() {
    zenMode = !zenMode;
    const event = new CustomEvent('zenModeChange', { detail: { zenMode } });
    window.dispatchEvent(event);
  }
  
  // Helper function to add console output
  function addConsoleOutput(message, level = 'info') {
    const timestamp = new Date().toLocaleTimeString();

    appState.update(state => {
      const entry = {
        timestamp,
        level,
        message
      };

      const updatedConsoleOutput = [...state.consoleOutput, entry];
      const trimmedConsoleOutput = updatedConsoleOutput.slice(-1000);

      return {
        ...state,
        consoleOutput: trimmedConsoleOutput
      };
    });
  }
  
  // Load tutorial files
  async function loadTutorialFiles(lang = null) {
    loadingTutorials = true;
    try {
      const url = lang ? `/api/tutorial/files?lang=${lang}` : '/api/tutorial/files';
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        
        if (lang) {
          tutorialFiles = data.files || [];
        } else {
          availableLanguages = Object.keys(data.languages || {}).map(code => ({
            code,
            name: code === 'en' ? 'English' : code === 'es' ? 'Español' : code.toUpperCase()
          }));
          
          if (data.languages && data.languages[selectedLanguage]) {
            tutorialFiles = data.languages[selectedLanguage];
          } else if (availableLanguages.length > 0) {
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
  
  async function changeLanguage(lang) {
    selectedLanguage = lang;
    await loadTutorialFiles(lang);
  }
  
  async function loadTutorialFile(file) {
    try {
      const response = await fetch(file.url);
      if (response.ok) {
        const content = await response.text();
        const newBuffer = {
          id: nextTabId++,
          name: file.name.replace('.py', ''),
          content: content,
          editing: false
        };
        tabs = [...tabs, newBuffer];
        activeTabId = newBuffer.id;
        
        if (editorComponent) {
          editorComponent.setValue(content);
          editorComponent.setCursor({ line: 0, ch: 0 });
          editorComponent.focus();
        }
      } else {
        console.error('Failed to load tutorial file');
      }
    } catch (error) {
      console.error('Error loading tutorial file:', error);
    }
  }
  
  // Session management
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
  
  async function ensureStartupFileSaved() {
    if (!startupFileTab) return null;
    
    if (!startupFileTab.startupFilePath) {
      try {
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
          startupFileTab.startupFilePath = result.path;
          
          tabs = tabs.map(tab => 
            tab.id === startupFileTab.id ? {...tab, startupFilePath: result.path} : tab
          );
          
          await loadStartupFiles();
          
          const newFile = startupFiles.find(file => file.name === startupFileTab.name);
          if (newFile) {
            currentSession.startupFile = newFile;
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
      await saveStartupFile(startupFileTab);
      return currentSession.startupFile;
    }
    
    return null;
  }
  
  async function doSaveSession(sessionName) {
    if (!sessionName.trim()) return;
    
    savingSession = true;
    try {
      await ensureStartupFileSaved();
      
      let combinedContent = "";
      
      const startupSeparator = '//' + '='.repeat(78);
      
      if (currentSession.startupFile && startupFileTab) {
        combinedContent += `${startupSeparator}\n`;
        combinedContent += `// STARTUP_FILE: ${currentSession.startupFile.name}\n`;
        combinedContent += `${startupSeparator}\n`;
        combinedContent += `${startupFileTab.content}\n\n`;
      } else if (startupFileTab) {
        combinedContent += `${startupSeparator}\n`;
        combinedContent += `// STARTUP_FILE: ${startupFileTab.name}\n`;
        combinedContent += `${startupSeparator}\n`;
        combinedContent += `${startupFileTab.content}\n\n`;
        
        const startupFile = startupFiles.find(f => f.name === startupFileTab.name);
        if (startupFile) {
          currentSession.startupFile = startupFile;
        }
      }
      
      const separator = '#'.repeat(80);
      const regularBuffers = tabs.filter(tab => !tab.isStartupFile);
      
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
        
        currentSession.name = result.filename;
        currentSession.modified = false;
        
        addConsoleOutput(`Session saved as ${result.filename}`, 'success');
        
        if (activeRightTab === 'sessions') {
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
  
  async function loadSessionFile(file) {
    try {
      const response = await fetch(file.url);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          currentSession = {
            name: file.name,
            startupFile: null,
            modified: false
          };
          
          const startupFileMatch = data.content.match(/\/\/={78}\n\/\/ STARTUP_FILE: (.+?)\n\/\/={78}\n([\s\S]+?)\n\n/);
          
          let startupFileName = null;
          let startupFileContent = null;
          let remainingContent = data.content;
          
          if (startupFileMatch) {
            startupFileName = startupFileMatch[1];
            startupFileContent = startupFileMatch[2];
            remainingContent = data.content.substring(startupFileMatch[0].length);
          }
          
          const separator = '#'.repeat(80);
          const parts = remainingContent.split(new RegExp(`\\n?${separator}\\n?`));
          
          tabs = [];
          let newTabId = 1;
          
          for (let i = 0; i < parts.length; i++) {
            const part = parts[i].trim();
            if (!part) continue;
            
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
                
                i++;
              }
            } else {
              tabs.push({
                id: newTabId++,
                name: `Untitled ${tabs.length + 1}`,
                content: part,
                editing: false,
                isStartupFile: false
              });
            }
          }
          
          if (startupFileName && startupFileContent) {
            await loadStartupFiles();
            
            const startupFile = startupFiles.find(f => f.name === startupFileName);
            
            if (startupFile) {
              currentSession.startupFile = startupFile;
              
              const startupTab = {
                id: newTabId++,
                name: startupFileName,
                content: startupFileContent,
                editing: false,
                isStartupFile: true,
                startupFilePath: startupFile.path
              };
              
              tabs = [startupTab, ...tabs];
              
              selectedStartupFile = startupFile;
            } else {
              console.warn(`Startup file ${startupFileName} not found in the system`);
              
              const localStartupTab = {
                id: newTabId++,
                name: startupFileName,
                content: startupFileContent,
                editing: false,
                isStartupFile: true,
                startupFilePath: null
              };
              
              tabs = [localStartupTab, ...tabs];
            }
          }
          
          if (tabs.length === 0) {
            tabs.push({
              id: newTabId,
              name: 'Untitled',
              content: '',
              editing: false,
              isStartupFile: false
            });
          }
          
          activeTabId = tabs[0].id;
          nextTabId = newTabId;
          
          if (editorComponent) {
            editorComponent.setValue(tabs[0].content);
            editorComponent.setCursor({ line: 0, ch: 0 });
            editorComponent.focus();
          }
          
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
  }
  
  // Startup files management
  async function loadStartupFiles() {
    loadingStartupFiles = true;
    try {
      const response = await fetch('/api/settings/user-directory/startup_files');
      if (response.ok) {
        const data = await response.json();
        startupFiles = data.files || [];
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
  
  async function initializeEditorWithDefaultStartupFile() {
    await loadStartupFiles();
    
    let defaultFile = startupFiles.find(file => file.name === 'startup.py');
    
    if (!defaultFile && startupFiles.length > 0) {
      defaultFile = startupFiles[0];
    }
    
    if (defaultFile) {
      await loadStartupFile(defaultFile);
    } else {
      const startupBuffer = {
        id: nextTabId++,
        name: 'startup.py',
        content: "# Renardo startup file\n# This file is loaded when Renardo starts\n# Add your custom code here\n",
        editing: false,
        isStartupFile: true,
        startupFilePath: null
      };
      
      tabs = [startupBuffer];
    }
    
    const codeBuffer = {
      id: nextTabId++,
      name: 'Untitled',
      content: ``,
      editing: false,
      isStartupFile: false
    };
    
    tabs = [...tabs, codeBuffer];
    
    activeTabId = codeBuffer.id;
  }
  
  async function loadStartupFile(file) {
    try {
      if (startupFileTab) {
        tabs = tabs.filter(tab => !tab.isStartupFile);
      }
      
      const response = await fetch(file.url);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          const newBuffer = {
            id: nextTabId++,
            name: file.name,
            content: data.content,
            editing: false,
            isStartupFile: true,
            startupFilePath: file.path
          };
          
          tabs = [newBuffer, ...tabs.filter(tab => !tab.isStartupFile)];
          activeTabId = newBuffer.id;
          
          if (editorComponent) {
            editorComponent.setValue(data.content);
            editorComponent.setCursor({ line: 0, ch: 0 });
            editorComponent.focus();
          }
          
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
      if (activeTabId === buffer.id && editorComponent) {
        buffer.content = editorComponent.getValue();
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
        tabs = tabs.map(tab => 
          tab.id === buffer.id ? {...tab, content: buffer.content} : tab
        );
        
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
    
    const existingTabByName = tabs.find(
      tab => tab.isStartupFile && tab.name === name
    );
    
    if (existingTabByName) {
      activeTabId = existingTabByName.id;
      if (editorComponent) {
        editorComponent.setValue(existingTabByName.content);
        editorComponent.focus();
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
        await loadStartupFiles();
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
  
  async function loadMusicExampleFile(file) {
    try {
      const response = await fetch(file.url);
      if (response.ok) {
        const content = await response.text();
        const newBuffer = {
          id: nextTabId++,
          name: file.name.replace('.py', ''),
          content: content,
          editing: false
        };
        tabs = [...tabs, newBuffer];
        activeTabId = newBuffer.id;
        
        if (editorComponent) {
          editorComponent.setValue(content);
          editorComponent.setCursor({ line: 0, ch: 0 });
          editorComponent.focus();
        }
      } else {
        console.error('Failed to load music example file');
      }
    } catch (error) {
      console.error('Error loading music example file:', error);
    }
  }
  
  // Insert preset code
  function insertPreset(code) {
    if (editorComponent) {
      editorComponent.insertAtCursor(code);
    }
  }
  
  onMount(() => {
    // Load saved settings
    const savedTheme = localStorage.getItem('editor-theme');
    if (savedTheme) {
      currentEditorTheme = savedTheme;
    }
    
    // Add global event listeners
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    
    // Load saved panel width
    const savedWidth = localStorage.getItem('rightPanelWidth');
    if (savedWidth) {
      rightPanelWidth = parseInt(savedWidth, 10);
    }
    
    // Load saved console height
    const savedConsoleHeight = localStorage.getItem('consoleHeight');
    if (savedConsoleHeight) {
      consoleHeight = parseFloat(savedConsoleHeight);
    }
    
    // Initialize editor with default startup file
    initializeEditorWithDefaultStartupFile();
    
    // Load tutorial files on mount
    loadTutorialFiles();
    
    // Load documentation if tab is active
    if (activeRightTab === 'documentation') {
      loadDocumentationFiles();
    }
    
    // Load music examples if tab is active
    if (activeRightTab === 'musicExamples') {
      loadMusicExampleFiles();
    }
    
    // Subscribe to appState changes
    const unsubscribe = appState.subscribe(state => {
      if (state.consoleOutput !== undefined) {
        consoleOutput = state.consoleOutput;
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
        
        const atLeastOneIncomplete = Object.values(initStatus).some(status => status === false);
        
        if (atLeastOneIncomplete && !modalDismissed) {
          showInitModal = true;
        } else {
          showInitModal = false;
        }
      }
    });
    
    // Set up keyboard shortcuts
    const handleKeyDown = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === '.') {
        event.preventDefault();
        stopMusic();
        return;
      }
      
      if (editorComponent && editorComponent.hasFocus && editorComponent.hasFocus()) {
        return;
      }
      
      if ((event.ctrlKey || event.metaKey) && !event.altKey && event.key === 'Enter') {
        event.preventDefault();
        executeCode();
      } 
      else if (event.altKey && !event.ctrlKey && !event.metaKey && event.key === 'Enter') {
        event.preventDefault();
        executeCurrentLine();
      }
      else if (event.altKey && event.metaKey && event.key === 'Enter') {
        event.preventDefault();
        executeCurrentLine();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    
    // Listen for code execution completion
    const handleCodeExecutionComplete = (event) => {
      const { requestId } = event.detail;
      if (requestId && editorComponent) {
        editorComponent.removeExecutionHighlight(requestId);
      }
    };
    
    window.addEventListener('codeExecutionComplete', handleCodeExecutionComplete);
    
    // Clean up
    return () => {
      unsubscribe();
      document.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('codeExecutionComplete', handleCodeExecutionComplete);
    };
  });
</script>

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
              if (editorComponent) {
                const allText = editorComponent.getAllText();
                sendCodeToExecute(allText.text, 'all', allText.from, allText.to);
              }
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
            bind:this={themeSelector}
            on:themeChange={(e) => {
              currentEditorTheme = e.detail.theme;
              if (editorComponent) {
                editorComponent.setTheme(e.detail.theme);
              }
            }}
          />
        </div>
      </div>
    </div>
  </div>
  {/if}

  <!-- Main content area with editor and console -->
  <div class="flex flex-1 overflow-hidden">
    <!-- Left side: Editor and console -->
    <div class="flex flex-col flex-1 overflow-hidden">
      <!-- Editor tabs -->
      <EditorTabs
        {tabs}
        {activeTabId}
        {nextTabId}
        {rightPanelOpen}
        on:switchTab={handleSwitchTab}
        on:startEditingName={handleStartEditingName}
        on:finishEditingName={handleFinishEditingName}
        on:cancelEditingName={handleCancelEditingName}
        on:closeBuffer={handleCloseBuffer}
        on:newBuffer={handleNewBuffer}
        on:saveStartupFile={handleSaveStartupFile}
        on:toggleRightPanel={() => rightPanelOpen = !rightPanelOpen}
      />
      
      <!-- Editor area with dynamic height -->
      <div class="flex-1 bg-base-100 overflow-hidden" style="height: {100 - consoleHeight}%;">
        <CodeMirrorEditor
          content={editorContent}
          theme={currentEditorTheme}
          {activeHighlights}
          bind:this={editorComponent}
          on:ready={handleEditorReady}
          on:change={handleEditorChange}
          on:execute={handleEditorExecute}
        />
      </div>
      
      <!-- Console output -->
      <ConsoleOutput
        {consoleOutput}
        {consoleHeight}
        {isVerticalResizing}
        {consoleMinimized}
        theme={currentEditorTheme}
        on:clear={handleConsoleClear}
        on:toggleMinimize={handleConsoleToggleMinimize}
        on:startResize={() => isVerticalResizing = true}
      />
    </div>

    <!-- Right side panel -->
    <RightPanel
      activeTab={activeRightTab}
      width={rightPanelWidth}
      open={rightPanelOpen}
      {tutorialFiles}
      {loadingTutorials}
      {selectedLanguage}
      {availableLanguages}
      {sessionFiles}
      {loadingSessions}
      {startupFiles}
      {loadingStartupFiles}
      {selectedStartupFile}
      currentSessionStartupFile={currentSession.startupFile}
      {musicExampleFiles}
      {loadingMusicExamples}
      {documentationFiles}
      {loadingDocumentation}
      {currentDocumentationContent}
      {selectedDocumentationFile}
      on:switchTab={handleRightPanelSwitchTab}
      on:close={() => rightPanelOpen = false}
      on:startResize={() => isResizing = true}
      on:changeLanguage={handleTutorialChangeLanguage}
      on:loadFile={(e) => {
        switch (activeRightTab) {
          case 'tutorial':
            handleTutorialLoadFile(e);
            break;
          case 'startupFiles':
            handleStartupLoadFile(e);
            break;
          case 'musicExamples':
            handleMusicExampleLoadFile(e);
            break;
          case 'documentation':
            handleDocumentationLoadFile(e);
            break;
        }
      }}
      on:loadSession={handleSessionLoadFile}
      on:openFolder={(e) => {
        switch (activeRightTab) {
          case 'sessions':
            handleSessionOpenFolder();
            break;
          case 'startupFiles':
            handleStartupOpenFolder();
            break;
        }
      }}
      on:createNew={handleStartupCreateNew}
      on:setDefault={handleStartupSetDefault}
      on:reload={handleMusicExampleReload}
      on:goHome={handleDocumentationGoHome}
    />
  </div>

  <!-- Error messages -->
  {#if $appState.error}
    <div class="alert alert-error rounded-none">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
      <span>Error: {$appState.error}</span>
    </div>
  {/if}
</div>

<!-- Modals -->
<InitializationModal
  show={showInitModal}
  {initStatus}
  on:dismiss={handleInitModalDismiss}
  on:goToInit={handleInitModalGoToInit}
/>

<SaveSessionModal
  show={showSaveModal}
  saving={savingSession}
  on:save={handleSaveSession}
  on:cancel={() => showSaveModal = false}
/>

<NewBufferModal
  show={showNewBufferModal}
  creating={false}
  on:create={handleCreateNewBuffer}
  on:cancel={() => showNewBufferModal = false}
/>

<CloseBufferModal
  show={showCloseBufferModal}
  bufferName={bufferToClose?.name || ''}
  on:close={closeBuffer}
  on:cancel={() => {
    showCloseBufferModal = false;
    bufferToClose = null;
  }}
/>

<style>
  /* Smooth transitions for layout changes */
  .flex {
    transition: all 0.3s ease;
  }
  
  /* Disable text selection during resize */
  :global(body.resizing) {
    user-select: none;
    cursor: col-resize;
  }
</style>