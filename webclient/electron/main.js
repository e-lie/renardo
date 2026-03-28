import { app, BrowserWindow, ipcMain } from 'electron';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { startServer, stopServer, isServerRunning } from './pythonManager.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// GPU acceleration flags for Nvidia on Linux
if (process.platform === 'linux') {
  app.commandLine.appendSwitch('use-gl', 'egl');
  app.commandLine.appendSwitch('enable-gpu-rasterization');
  app.commandLine.appendSwitch('ignore-gpu-blocklist');
  app.commandLine.appendSwitch('enable-features', 'VaapiVideoDecoder,VaapiIgnoreDriverChecks,Vulkan');
}

let mainWindow = null;

async function createWindow() {
  console.log('Creating main window...');

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: join(__dirname, 'preload.js'),
      webSecurity: true
    },
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default'
  });

  mainWindow.once('ready-to-show', () => {
    console.log('Window ready to show');
    mainWindow.show();
    if (mainWindow) {
      mainWindow.focus();
    }
  });

  mainWindow.on('closed', () => {
    console.log('Main window closed');
    mainWindow = null;
  });

  try {
    console.log('Starting backend server...');
    await startServer();
    console.log('Backend server started successfully');
  } catch (error) {
    console.error('Failed to start backend server:', error);
    const { dialog } = await import('electron');
    await dialog.showErrorBox('Server Error',
      `Failed to start the backend server:\n\n${error.message}\n\nThe application will now quit.`);
    app.quit();
    return;
  }

  console.log('Loading application...');
  try {
    // In dev mode: Vite dev server on 3001, backend on 8000
    // In packaged mode: uvicorn serves both static files and API on 8000
    const url = app.isPackaged ? 'http://localhost:8000' : 'http://localhost:3001';
    await mainWindow.loadURL(url);
    if (!app.isPackaged) {
      mainWindow.webContents.openDevTools();
    }
  } catch (error) {
    console.error('Failed to load application:', error);
  }
}

function setupIpcHandlers() {
  ipcMain.handle('server-status', async () => {
    return isServerRunning() ? 'running' : 'stopped';
  });

  ipcMain.on('window-minimize', () => {
    if (mainWindow) mainWindow.minimize();
  });

  ipcMain.on('window-maximize', () => {
    if (mainWindow) {
      if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
      } else {
        mainWindow.maximize();
      }
    }
  });

  ipcMain.on('window-close', () => {
    if (mainWindow) mainWindow.close();
  });

  ipcMain.handle('app-version', () => app.getVersion());
  ipcMain.handle('app-path', () => app.getAppPath());
}

app.whenReady().then(async () => {
  console.log('Electron app ready');
  setupIpcHandlers();
  await createWindow();

  app.on('activate', async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      await createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  console.log('All windows closed');
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  console.log('App is about to quit');
  if (isServerRunning()) {
    console.log('Stopping server before quit...');
    stopServer();
  }
});

app.on('will-quit', (event) => {
  console.log('App will quit');
  if (isServerRunning()) {
    event.preventDefault();
    setTimeout(() => app.quit(), 1000);
  }
});

app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    const { shell } = require('electron');
    shell.openExternal(navigationUrl);
  });
});

export { mainWindow };
