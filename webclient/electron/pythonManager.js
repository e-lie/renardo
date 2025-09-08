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
  if (app.isPackaged) {
    // In packaged app: python is in resources
    return join(process.resourcesPath, 'python', 'bin', 'python3.12');
  } else {
    // In development: python is in webclient/python
    return join(__dirname, '..', 'python', 'bin', 'python3.12');
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
 * Install required dependencies in the bundled Python
 * In development, we'll run with the system Python setup
 */
async function installDependencies() {
  if (app.isPackaged) {
    const pythonPath = findPython();
    console.log('Installing dependencies in packaged app...');
    
    return new Promise((resolve, reject) => {
      // Install all pip packages needed by renardo (from pyproject.toml dependencies)
      const installProcess = spawn(pythonPath, [
        '-m', 'pip', 'install',
        'midiutil', 'tomli', 'tomli-w', 'requests', 'psutil', 'indexed',
        'python-rtmidi', 'ttkbootstrap', 'textual<3', 'fastnumbers>=5.1.1',
        'mido>=1.3.3', 'flask>=3.1.0', 'flask-sock>=0.7.0', 'flask-cors>=3.0.10',
        'websockets>=10.4', 'gunicorn', 'gevent', 'gevent-websocket',
        'markdown>=3.5.1', 'python-reapy>=0.10.0', 'python-osc>=1.8.3'
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
    
    // Start the Flask server by running renardo module
    // Set PYTHONPATH to the parent directory containing the renardo module
    pythonProcess = spawn(pythonExecutable, ['-m', 'renardo', '--no-browser'], {
      cwd: pythonPath,
      env: {
        ...process.env,
        PYTHONPATH: pythonPath,
        RENARDO_WEB_MODE: 'electron'
      }
    });
  } else {
    // Development: use system Python with uv
    renardoPath = findRenardoPath();
    pythonPath = findPythonPath();
    console.log('Development mode');
    console.log('Renardo source path:', renardoPath);
    console.log('Python module path:', pythonPath);
    
    // Use uv to run renardo with proper environment
    pythonProcess = spawn('uv', ['run', 'python', '-m', 'renardo', '--no-browser'], {
      cwd: pythonPath,
      env: {
        ...process.env,
        RENARDO_WEB_MODE: 'electron'
      }
    });
  }
  
  console.log('Starting Flask server...');
  
  pythonProcess.stdout.on('data', (data) => {
    const output = data.toString();
    console.log(`Flask stdout: ${output}`);
  });
  
  pythonProcess.stderr.on('data', (data) => {
    const output = data.toString();
    console.log(`Flask stderr: ${output}`);
  });
  
  pythonProcess.on('close', (code) => {
    console.log(`Flask process exited with code ${code}`);
    pythonProcess = null;
  });
  
  pythonProcess.on('error', (error) => {
    console.error('Failed to start Flask process:', error);
    pythonProcess = null;
  });
  
  // Give Flask a moment to start, then proceed
  console.log('Giving Flask server time to start...');
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Optional: try health check once but don't fail if it doesn't work
  try {
    const result = await checkHealth();
    if (result) {
      console.log('Flask server confirmed ready!');
    } else {
      console.log('Flask server not responding to health check, but proceeding anyway...');
    }
  } catch (error) {
    console.log('Health check failed, but proceeding anyway...');
  }
  
  return true;
}

/**
 * Wait for Flask server to be ready
 */
async function waitForFlask(maxAttempts = 30) {
  console.log('Waiting for Flask server to be ready...');
  
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const result = await checkHealth();
      if (result) {
        console.log('Flask server is ready!');
        return true;
      }
    } catch (error) {
      // Server not ready yet, continue waiting
    }
    
    console.log(`Attempt ${i + 1}/${maxAttempts}: Flask not ready, waiting...`);
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error(`Flask server failed to start after ${maxAttempts} attempts`);
}

/**
 * Check Flask health using http module
 */
function checkHealth() {
  return new Promise((resolve, reject) => {
    const req = http.get('http://localhost:12345/api/health', (res) => {
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
 * Stop the Flask server
 */
function stopFlaskServer() {
  if (pythonProcess) {
    console.log('Stopping Flask server...');
    pythonProcess.kill('SIGTERM');
    
    // Force kill after 5 seconds if still running
    setTimeout(() => {
      if (pythonProcess && !pythonProcess.killed) {
        console.log('Force killing Flask process...');
        pythonProcess.kill('SIGKILL');
      }
    }, 5000);
    
    pythonProcess = null;
  }
}

/**
 * Check if Flask server is running
 */
function isFlaskRunning() {
  return pythonProcess !== null && !pythonProcess.killed;
}

export {
  startFlaskServer,
  stopFlaskServer,
  isFlaskRunning
};