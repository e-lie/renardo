import { app, BrowserWindow, ipcMain } from 'electron';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { startFlaskServer, stopFlaskServer, isFlaskRunning } from './pythonManager.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Keep a global reference of the window object
let mainWindow = null;

/**
 * Create the main application window
 */
async function createWindow() {
  console.log('Creating main window...');
  
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    show: false, // Don't show until ready
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: join(__dirname, 'preload.js'),
      webSecurity: true
    },
    icon: join(__dirname, '../assets/icon.png'),
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default'
  });
  
  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    console.log('Window ready to show');
    mainWindow.show();
    
    // Focus on the window when it's shown
    if (mainWindow) {
      mainWindow.focus();
    }
  });
  
  // Handle window closed
  mainWindow.on('closed', () => {
    console.log('Main window closed');
    mainWindow = null;
  });
  
  // Start FastAPI server first
  try {
    console.log('Starting FastAPI server...');
    await startFlaskServer();
    console.log('FastAPI server started successfully');
  } catch (error) {
    console.error('Failed to start FastAPI server:', error);
    
    // Show error dialog and quit
    const { dialog } = await import('electron');
    await dialog.showErrorBox('FastAPI Server Error', 
      `Failed to start the FastAPI server:\n\n${error.message}\n\nThe application will now quit.`);
    app.quit();
    return;
  }
  
  // Load the app from the built frontend
  console.log('Loading from built frontend...');
  try {
    if (app.isPackaged) {
      // In production, load from the packaged static files in resources
      await mainWindow.loadFile(join(process.resourcesPath, 'renardo/webserver_fresh/static/index.html'));
    } else {
      // In development, load from Vite dev server
      await mainWindow.loadURL('http://localhost:3001');
    }
    
    // Open DevTools in development
    if (!app.isPackaged) {
      mainWindow.webContents.openDevTools();
    }
  } catch (error) {
    console.error('Failed to load frontend:', error);
    console.log('Make sure frontend is built or Vite dev server is running on port 3001');
  }
}

/**
 * Set up IPC handlers
 */
function setupIpcHandlers() {
  // FastAPI server status
  ipcMain.handle('flask-status', async () => {
    return isFlaskRunning() ? 'running' : 'stopped';
  });
  
  // Window controls
  ipcMain.on('window-minimize', () => {
    if (mainWindow) {
      mainWindow.minimize();
    }
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
    if (mainWindow) {
      mainWindow.close();
    }
  });
  
  // App info
  ipcMain.handle('app-version', () => {
    return app.getVersion();
  });
  
  ipcMain.handle('app-path', () => {
    return app.getAppPath();
  });
}

/**
 * App event handlers
 */

// This method will be called when Electron has finished initialization
app.whenReady().then(async () => {
  console.log('Electron app ready');
  
  // Set up IPC handlers
  setupIpcHandlers();
  
  // Create the main window
  await createWindow();
  
  // macOS: Re-create window when dock icon is clicked
  app.on('activate', async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      await createWindow();
    }
  });
});

// Quit when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  console.log('All windows closed');
  
  // On macOS, keep the app running even when all windows are closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Clean up before quitting
app.on('before-quit', (event) => {
  console.log('App is about to quit');
  
  // Stop FastAPI server
  if (isFlaskRunning()) {
    console.log('Stopping FastAPI server before quit...');
    stopFlaskServer();
  }
});

// Handle app quit
app.on('will-quit', (event) => {
  console.log('App will quit');
  
  // Give FastAPI server time to stop gracefully
  if (isFlaskRunning()) {
    event.preventDefault();
    setTimeout(() => {
      app.quit();
    }, 1000);
  }
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    // Prevent opening new windows
    event.preventDefault();
    
    // Optionally, open in external browser
    const { shell } = require('electron');
    shell.openExternal(navigationUrl);
  });
});

// Handle certificate errors
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  // Allow localhost certificates in development
  if (url.startsWith('https://localhost') || url.startsWith('https://127.0.0.1')) {
    event.preventDefault();
    callback(true);
  } else {
    callback(false);
  }
});

// Export for testing
export { mainWindow };