const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  isElectron: () => true,
  getAppVersion: () => ipcRenderer.invoke('app-version'),
  getAppPath: () => ipcRenderer.invoke('app-path'),
  getServerStatus: () => ipcRenderer.invoke('server-status'),
  windowMinimize: () => ipcRenderer.send('window-minimize'),
  windowMaximize: () => ipcRenderer.send('window-maximize'),
  windowClose: () => ipcRenderer.send('window-close'),
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath, content) => ipcRenderer.invoke('write-file', filePath, content),
  saveFileDialog: (options) => ipcRenderer.invoke('save-file-dialog', options),
  openFileDialog: (options) => ipcRenderer.invoke('open-file-dialog', options),
  platform: process.platform,
  onServerStatusChanged: (callback) => {
    const subscription = (event, status) => callback(status);
    ipcRenderer.on('server-status-changed', subscription);
    return () => ipcRenderer.removeListener('server-status-changed', subscription);
  },
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});

console.log('Renardo Electron preload script loaded');
