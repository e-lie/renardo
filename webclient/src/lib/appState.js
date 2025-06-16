import { writable } from 'svelte/store';

// Create stores for application state
export const appState = writable({
  counter: 0,
  welcomeText: 'Loading...',
  connected: false,
  error: null,
  // Backend OS information
  backendOS: null,
  // Add Renardo initialization state
  renardoInit: {
    superColliderClasses: false,
    sclangCode: false,
    samples: false,
    instruments: false,
    reaperPack: false,
    startupFiles: false
  },
  // Add runtime status
  runtimeStatus: {
    scBackendRunning: false,
    scBackendStartupCode: 'Renardo.start; Renardo.midi;'
  },
  // Add log messages array
  logMessages: [],
  // Add console output array
  consoleOutput: [],
  // Last received message for event detection
  _lastMessage: null
});