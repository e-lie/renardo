import { writable, get } from 'svelte/store';

// Create stores for application state with thematic subsections
export const appState = writable({
  // ========== CONNECTION & BACKEND ==========
  connection: {
    connected: false,
    error: null,
    backendOS: null,
    _lastMessage: null
  },

  // ========== RENARDO RUNTIME ==========
  renardo: {
    // Initialization status
    init: {
      superColliderClasses: false,
      sclangCode: false,
      samples: false,
      instruments: false,
      reaperPack: false,
      startupFiles: false
    },
    // Runtime status
    runtime: {
      scBackendRunning: false,
      scBackendStartupCode: 'Renardo.start; Renardo.midi;'
    },
    // Console and logging
    console: {
      output: [],
      logMessages: []
    }
  },

  // ========== CODE EDITOR ==========
  editor: {
    // Editor settings
    settings: {
      theme: 'dracula',
      font: 'fira-code',
      showLineNumbers: true,
      vimModeEnabled: false,
      showActionButtons: true,
      showShortcuts: true
    },
    // UI state
    ui: {
      zenMode: false,
      rightPanelOpen: true,
      rightPanelWidth: 384,
      activeRightTab: 'tutorial',
      consoleHeight: 30,
      consoleMinimized: false
    },
    // Session management
    session: {
      name: 'Untitled Session',
      startupFile: null,
      modified: false,
      tabs: [],
      activeTabId: 1,
      nextTabId: 2
    },
    // Execution state
    execution: {
      activeHighlights: {},
      lastExecutionId: null
    }
  },

  // ========== COLLECTIONS ==========
  collections: {
    samples: {
      availablePacks: [],
      loadedPacks: [],
      loading: false,
      error: null
    },
    instruments: {
      available: [],
      loaded: [],
      loading: false,
      error: null
    }
  },

  // ========== CONFIGURATION ==========
  configuration: {
    userDirectory: '',
    settings: {},
    loading: false,
    error: null,
    modified: false
  },

  // ========== AUDIO BACKEND ==========
  audioBackend: {
    current: 'supercollider',
    status: 'stopped',
    devices: [],
    selectedDevice: null,
    loading: false,
    error: null
  },

  // ========== APPLICATION ==========
  app: {
    currentRoute: 'editor',
    theme: 'default',
    welcomeText: 'Loading...',
    counter: 0 // For compatibility
  }
});

// Helper functions for state management
export const stateHelpers = {
  // Update a specific section of the state
  updateSection: (section, updates) => {
    appState.update(state => ({
      ...state,
      [section]: {
        ...state[section],
        ...updates
      }
    }));
  },

  // Update nested section (e.g., 'editor.settings')
  updateNestedSection: (section, subsection, updates) => {
    appState.update(state => ({
      ...state,
      [section]: {
        ...state[section],
        [subsection]: {
          ...state[section][subsection],
          ...updates
        }
      }
    }));
  },

  // Get current state value
  getCurrentState: () => {
    return get(appState);
  },

  // Reset a specific section
  resetSection: (section, defaultValue = {}) => {
    appState.update(state => ({
      ...state,
      [section]: defaultValue
    }));
  },

  // Initialize editor settings from localStorage
  initializeEditorSettings: () => {
    const theme = localStorage.getItem('editor-theme') || 'dracula';
    const font = localStorage.getItem('editor-font-family') || 'fira-code';
    const showLineNumbers = localStorage.getItem('editor-show-line-numbers') !== 'false';
    const vimModeEnabled = localStorage.getItem('editor-vim-mode') === 'true';
    const showActionButtons = localStorage.getItem('editor-show-action-buttons') !== 'false';
    const showShortcuts = localStorage.getItem('editor-show-shortcuts') !== 'false';

    stateHelpers.updateNestedSection('editor', 'settings', {
      theme,
      font,
      showLineNumbers,
      vimModeEnabled,
      showActionButtons,
      showShortcuts
    });
  },
  
  // Initialize editor UI state from localStorage
  initializeEditorUI: () => {
    // Try to load UI state from localStorage first
    try {
      const savedUI = localStorage.getItem('editor-ui');
      if (savedUI) {
        const parsedUI = JSON.parse(savedUI);
        stateHelpers.updateNestedSection('editor', 'ui', parsedUI);
        return;
      }
    } catch (error) {
      console.warn('Failed to load saved UI state:', error);
    }
    
    // Fallback to individual localStorage items or defaults
    const rightPanelWidth = parseInt(localStorage.getItem('rightPanelWidth'), 10) || 384;
    const consoleHeight = parseFloat(localStorage.getItem('consoleHeight')) || 30;
    const rightPanelOpen = localStorage.getItem('rightPanelOpen') !== 'false';
    const activeRightTab = localStorage.getItem('activeRightTab') || 'tutorial';
    const consoleMinimized = localStorage.getItem('consoleMinimized') === 'true';
    const zenMode = localStorage.getItem('zenMode') === 'true';

    stateHelpers.updateNestedSection('editor', 'ui', {
      zenMode,
      rightPanelOpen,
      rightPanelWidth,
      activeRightTab,
      consoleHeight,
      consoleMinimized
    });
  },

  // Initialize default editor session (only if no session exists)
  initializeEditorSession: () => {
    const currentState = get(appState);
    
    // Try to load session from localStorage first
    try {
      const savedSession = localStorage.getItem('editor-session');
      if (savedSession) {
        const parsedSession = JSON.parse(savedSession);
        if (parsedSession.tabs && parsedSession.tabs.length > 0) {
          stateHelpers.updateNestedSection('editor', 'session', parsedSession);
          return;
        }
      }
    } catch (error) {
      console.warn('Failed to load saved session:', error);
    }
    
    // Only initialize with default if there's no existing session and no saved session
    if (!currentState.editor.session.tabs || currentState.editor.session.tabs.length === 0) {
      const defaultTab = {
        id: 1,
        name: 'Untitled',
        content: '',
        editing: false,
        isStartupFile: false
      };

      stateHelpers.updateNestedSection('editor', 'session', {
        tabs: [defaultTab],
        activeTabId: 1,
        nextTabId: 2,
        name: 'Untitled Session',
        modified: false
      });
    }
  },
  
  // Save editor session to localStorage
  saveEditorSession: () => {
    const currentState = get(appState);
    try {
      localStorage.setItem('editor-session', JSON.stringify(currentState.editor.session));
    } catch (error) {
      console.warn('Failed to save session:', error);
    }
  },
  
  // Save editor UI state to localStorage
  saveEditorUI: () => {
    const currentState = get(appState);
    try {
      localStorage.setItem('editor-ui', JSON.stringify(currentState.editor.ui));
    } catch (error) {
      console.warn('Failed to save UI state:', error);
    }
  }
};