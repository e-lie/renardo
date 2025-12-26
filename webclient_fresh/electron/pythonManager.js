import { app } from 'electron';
import { spawn } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import http from 'http';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let pythonProcess = null;

/**
 * Find the Python executable path based on environment
 */
function findPython() {
  const isWindows = process.platform === 'win32';
  
  if (app.isPackaged) {
    // In packaged app: python is in resources
    if (isWindows) {
      return join(process.resourcesPath, 'python', 'python.exe');
    } else {
      return join(process.resourcesPath, 'python', 'bin', 'python3.12');
    }
  } else {
    // In development: python is in webclient_fresh/python
    if (isWindows) {
      return join(__dirname, '..', 'python', 'python.exe');
    } else {
      return join(__dirname, '..', 'python', 'bin', 'python3.12');
    }
  }
}

/**
 * Find the Renardo source path
 */
function findRenardoPath() {
  if (app.isPackaged) {
    // In packaged app: renardo source is in resources
    return join(process.resourcesPath, 'renardo');
  } else {
    // In development: use the actual source directory
    return join(__dirname, '..', '..', 'src', 'renardo');
  }
}

/**
 * Find the Python path (parent directory containing renardo module)
 */
function findPythonPath() {
  if (app.isPackaged) {
    // In packaged app: resources directory contains the renardo module
    return process.resourcesPath;
  } else {
    // In development: src directory contains the renardo module
    return join(__dirname, '..', '..', 'src');
  }
}

/**
 * Get the local site-packages directory for the bundled Python
 */
function getLocalSitePackages() {
  // Create a local site-packages directory in app's temp space
  const tempDir = app.getPath('temp');
  return join(tempDir, 'renardo-fresh-electron', 'site-packages');
}

/**
 * Install required dependencies in the bundled Python
 * In development, we'll run with the system Python setup
 */
async function installDependencies() {
  if (app.isPackaged) {
    const pythonPath = findPython();
    const localSitePackages = getLocalSitePackages();
    
    console.log('Installing dependencies in packaged app...');
    console.log('Local site-packages:', localSitePackages);
    
    return new Promise((resolve, reject) => {
      // Install all pip packages needed by renardo (from pyproject.toml dependencies)
      // Use --target to install to a specific directory instead of user directory
      const installProcess = spawn(pythonPath, [
        '-m', 'pip', 'install', '--target', localSitePackages,
        'midiutil', 'tomli', 'tomli-w', 'requests', 'psutil', 'indexed',
        'python-rtmidi', 'ttkbootstrap', 'textual<3', 'fastnumbers>=5.1.1',
        'mido>=1.3.3', 'flask>=3.1.0', 'flask-sock>=0.7.0', 'flask-cors>=3.0.10',
        'websockets>=10.4', 'gunicorn', 'gevent', 'gevent-websocket',
        'markdown>=3.5.1', 'python-reapy>=0.10.0', 'python-osc>=1.8.3',
        'fastapi>=0.104.1', 'uvicorn[standard]>=0.24.0'
      ]);
      
      installProcess.stdout.on('data', (data) => {
        console.log(`Pip install: ${data.toString()}`);
      });
      
      installProcess.stderr.on('data', (data) => {
        console.error(`Pip install error: ${data.toString()}`);
      });
      
      installProcess.on('close', (code) => {
        if (code === 0) {
          console.log('Dependencies installed successfully');
          resolve();
        } else {
          reject(new Error(`Failed to install dependencies, exit code: ${code}`));
        }
      });
    });
  } else {
    console.log('Development mode: skipping dependency installation');
    return Promise.resolve();
  }
}

/**
 * Start the Flask server
 */
async function startFlaskServer() {
  let pythonExecutable, renardoPath, pythonPath;
  
  if (app.isPackaged) {
    // Production: use embedded Python
    pythonExecutable = findPython();
    renardoPath = findRenardoPath();
    pythonPath = findPythonPath();
    
    console.log('Production mode');
    console.log('Python executable:', pythonExecutable);
    console.log('Renardo source path:', renardoPath);
    console.log('Python module path:', pythonPath);
    
    try {
      await installDependencies();
    } catch (error) {
      console.error('Failed to install dependencies:', error);
      throw error;
    }
    
    // Start the FastAPI server by running renardo webclient mode
    // Set PYTHONPATH to include both the renardo module and local site-packages
    const localSitePackages = getLocalSitePackages();
    const pathSeparator = process.platform === 'win32' ? ';' : ':';
    const pythonPathEnv = `${localSitePackages}${pathSeparator}${pythonPath}`;
    
    pythonProcess = spawn(pythonExecutable, ['-m', 'uvicorn', 'renardo.webserver_fresh.app:app', '--host', '0.0.0.0', '--port', '8000'], {
      cwd: pythonPath,
      env: {
        ...process.env,
        PYTHONPATH: pythonPathEnv,
        RENARDO_WEB_MODE: 'electron-fresh'
      }
    });
  } else {
    // Development: use system Python with uv
    renardoPath = findRenardoPath();
    pythonPath = findPythonPath();
    console.log('Development mode');
    console.log('Renardo source path:', renardoPath);
    console.log('Python module path:', pythonPath);
    
    // Use uv to run FastAPI server with proper environment
    pythonProcess = spawn('uv', ['run', 'uvicorn', 'renardo.webserver_fresh.app:app', '--host', '0.0.0.0', '--port', '8000'], {
      cwd: pythonPath,
      env: {
        ...process.env,
        RENARDO_WEB_MODE: 'electron-fresh'
      }
    });
  }
  
  console.log('Starting FastAPI server...');
  
  pythonProcess.stdout.on('data', (data) => {
    const output = data.toString();
    console.log(`FastAPI stdout: ${output}`);
  });
  
  pythonProcess.stderr.on('data', (data) => {
    const output = data.toString();
    console.log(`FastAPI stderr: ${output}`);
  });
  
  pythonProcess.on('close', (code) => {
    console.log(`FastAPI process exited with code ${code}`);
    pythonProcess = null;
  });
  
  pythonProcess.on('error', (error) => {
    console.error('Failed to start FastAPI process:', error);
    pythonProcess = null;
  });
  
  // Give FastAPI a moment to start, then proceed
  console.log('Giving FastAPI server time to start...');
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Optional: try health check once but don't fail if it doesn't work
  try {
    const result = await checkHealth();
    if (result) {
      console.log('FastAPI server confirmed ready!');
    } else {
      console.log('FastAPI server not responding to health check, but proceeding anyway...');
    }
  } catch (error) {
    console.log('Health check failed, but proceeding anyway...');
  }
  
  return true;
}

/**
 * Wait for FastAPI server to be ready
 */
async function waitForFlask(maxAttempts = 30) {
  console.log('Waiting for FastAPI server to be ready...');
  
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const result = await checkHealth();
      if (result) {
        console.log('FastAPI server is ready!');
        return true;
      }
    } catch (error) {
      // Server not ready yet, continue waiting
    }
    
    console.log(`Attempt ${i + 1}/${maxAttempts}: FastAPI not ready, waiting...`);
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error(`FastAPI server failed to start after ${maxAttempts} attempts`);
}

/**
 * Check FastAPI health using http module
 */
function checkHealth() {
  return new Promise((resolve, reject) => {
    const req = http.get('http://localhost:8000/health', (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log('Health check successful:', data);
          resolve(true);
        } else {
          resolve(false);
        }
      });
    });
    
    req.on('error', (error) => {
      resolve(false); // Don't reject, just return false to continue trying
    });
    
    req.setTimeout(2000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

/**
 * Stop the FastAPI server
 */
function stopFlaskServer() {
  if (pythonProcess) {
    console.log('Stopping FastAPI server...');
    pythonProcess.kill('SIGTERM');
    
    // Force kill after 5 seconds if still running
    setTimeout(() => {
      if (pythonProcess && !pythonProcess.killed) {
        console.log('Force killing FastAPI process...');
        pythonProcess.kill('SIGKILL');
      }
    }, 5000);
    
    pythonProcess = null;
  }
}

/**
 * Check if FastAPI server is running
 */
function isFlaskRunning() {
  return pythonProcess !== null && !pythonProcess.killed;
}

export {
  startFlaskServer,
  stopFlaskServer,
  isFlaskRunning
};