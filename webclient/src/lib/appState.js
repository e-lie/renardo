import { writable } from 'svelte/store';

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
    let currentState;
    appState.subscribe(state => currentState = state)();
    return currentState;
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
    const rightPanelWidth = parseInt(localStorage.getItem('rightPanelWidth'), 10) || 384;
    const consoleHeight = parseFloat(localStorage.getItem('consoleHeight')) || 30;

    stateHelpers.updateNestedSection('editor', 'settings', {
      theme,
      font,
      showLineNumbers,
      vimModeEnabled,
      showActionButtons,
      showShortcuts
    });

    stateHelpers.updateNestedSection('editor', 'ui', {
      rightPanelWidth,
      consoleHeight
    });
  },

  // Initialize default editor session
  initializeEditorSession: () => {
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
};