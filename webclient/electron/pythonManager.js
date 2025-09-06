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
 * Install required dependencies in the bundled Python
 * In development, we'll run with the system Python setup
 */
async function installDependencies() {
  if (app.isPackaged) {
    const pythonPath = findPython();
    console.log('Installing dependencies in packaged app...');
    
    return new Promise((resolve, reject) => {
      // Install pip packages needed by renardo
      const installProcess = spawn(pythonPath, [
        '-m', 'pip', 'install', 
        'flask', 'flask-sock', 'flask-cors', 'websockets'
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
  let pythonPath, renardoPath;
  
  if (app.isPackaged) {
    // Production: use embedded Python
    pythonPath = findPython();
    renardoPath = findRenardoPath();
    
    console.log('Production mode');
    console.log('Python path:', pythonPath);
    console.log('Renardo path:', renardoPath);
    
    try {
      await installDependencies();
    } catch (error) {
      console.error('Failed to install dependencies:', error);
      throw error;
    }
    
    // Start the Flask server by running renardo module
    pythonProcess = spawn(pythonPath, ['-m', 'renardo', '--no-browser'], {
      cwd: renardoPath,
      env: {
        ...process.env,
        PYTHONPATH: renardoPath,
        RENARDO_WEB_MODE: 'electron'
      }
    });
  } else {
    // Development: use system Python with uv
    renardoPath = findRenardoPath();
    console.log('Development mode');
    console.log('Renardo path:', renardoPath);
    
    // Use uv to run renardo with proper environment
    pythonProcess = spawn('uv', ['run', 'python', '-m', 'renardo', '--no-browser'], {
      cwd: renardoPath,
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