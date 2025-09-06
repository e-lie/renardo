import { contextBridge, ipcRenderer } from 'electron';

/**
 * Preload script for secure communication between renderer and main process
 * This script runs in a privileged context and exposes safe APIs to the renderer
 */

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Environment detection
  isElectron: () => true,
  
  // App information
  getAppVersion: () => ipcRenderer.invoke('app-version'),
  getAppPath: () => ipcRenderer.invoke('app-path'),
  
  // Flask server status
  getFlaskStatus: () => ipcRenderer.invoke('flask-status'),
  
  // Window controls
  windowMinimize: () => ipcRenderer.send('window-minimize'),
  windowMaximize: () => ipcRenderer.send('window-maximize'),
  windowClose: () => ipcRenderer.send('window-close'),
  
  // File system operations (for future use)
  // These would be implemented as IPC handlers in main.js
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath, content) => ipcRenderer.invoke('write-file', filePath, content),
  saveFileDialog: (options) => ipcRenderer.invoke('save-file-dialog', options),
  openFileDialog: (options) => ipcRenderer.invoke('open-file-dialog', options),
  
  // System information
  platform: process.platform,
  
  // Event listeners for renderer to listen to main process events
  onFlaskStatusChanged: (callback) => {
    const subscription = (event, status) => callback(status);
    ipcRenderer.on('flask-status-changed', subscription);
    
    // Return unsubscribe function
    return () => {
      ipcRenderer.removeListener('flask-status-changed', subscription);
    };
  },
  
  // Remove all listeners for a specific channel (cleanup)
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

// Log that preload script has loaded
console.log('Renardo Electron preload script loaded');

// Version information
console.log(`Electron version: ${process.versions.electron}`);
console.log(`Node version: ${process.versions.node}`);
console.log(`Chrome version: ${process.versions.chrome}`);