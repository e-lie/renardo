import { app } from 'electron';
import { spawn } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import http from 'http';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let serverProcess = null;

function findPython() {
  const isWindows = process.platform === 'win32';

  if (app.isPackaged) {
    if (isWindows) {
      return join(process.resourcesPath, 'python', 'python.exe');
    } else {
      return join(process.resourcesPath, 'python', 'bin', 'python3.12');
    }
  } else {
    if (isWindows) {
      return join(__dirname, '..', 'python', 'python.exe');
    } else {
      return join(__dirname, '..', 'python', 'bin', 'python3.12');
    }
  }
}

function findRenardoPath() {
  if (app.isPackaged) {
    return join(process.resourcesPath, 'renardo');
  } else {
    return join(__dirname, '..', '..', 'src', 'renardo');
  }
}

function findPythonPath() {
  if (app.isPackaged) {
    return process.resourcesPath;
  } else {
    return join(__dirname, '..', '..', 'src');
  }
}

function findStaticFolder() {
  if (app.isPackaged) {
    return join(process.resourcesPath, 'renardo', 'webserver', 'static');
  } else {
    return join(__dirname, '..', 'dist');
  }
}

function getLocalSitePackages() {
  const tempDir = app.getPath('temp');
  return join(tempDir, 'renardo-electron', 'site-packages');
}

async function installDependencies() {
  if (app.isPackaged) {
    const pythonPath = findPython();
    const localSitePackages = getLocalSitePackages();
    const fs = await import('fs');
    const markerFile = join(localSitePackages, '.deps-installed');

    // Check if dependencies are already installed
    if (fs.existsSync(markerFile)) {
      console.log('Dependencies already installed, skipping...');
      return Promise.resolve();
    }

    console.log('Installing dependencies in packaged app...');
    console.log('Local site-packages:', localSitePackages);

    return new Promise((resolve, reject) => {
      const installProcess = spawn(pythonPath, [
        '-m', 'pip', 'install', '--target', localSitePackages,
        'midiutil', 'tomli', 'tomli-w', 'requests', 'psutil', 'indexed',
        'python-rtmidi', 'ttkbootstrap', 'textual<3', 'fastnumbers>=5.1.1',
        'mido>=1.3.3', 'fastapi>=0.109.0', 'uvicorn>=0.27.0',
        'websockets>=10.4', 'markdown>=3.5.1', 'python-reapy>=0.10.0',
        'python-osc>=1.8.3', 'diskcache>=5.6.0', 'strawberry-graphql>=0.217.0',
        'pydantic>=2.0.0', 'jinja2>=3.1.0'
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
          // Create marker file to skip install next time
          fs.writeFileSync(markerFile, new Date().toISOString());
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

async function startServer() {
  let pythonExecutable, renardoPath, pythonPath, staticFolder;

  if (app.isPackaged) {
    pythonExecutable = findPython();
    renardoPath = findRenardoPath();
    pythonPath = findPythonPath();
    staticFolder = findStaticFolder();

    console.log('Production mode');
    console.log('Python executable:', pythonExecutable);
    console.log('Renardo source path:', renardoPath);
    console.log('Python module path:', pythonPath);
    console.log('Static folder:', staticFolder);

    try {
      await installDependencies();
    } catch (error) {
      console.error('Failed to install dependencies:', error);
      throw error;
    }

    const localSitePackages = getLocalSitePackages();
    const pathSeparator = process.platform === 'win32' ? ';' : ':';
    const pythonPathEnv = `${localSitePackages}${pathSeparator}${pythonPath}`;

    // Run uvicorn with webserver
    serverProcess = spawn(pythonExecutable, [
      '-m', 'uvicorn',
      'renardo.webserver.app:app',
      '--host', '0.0.0.0',
      '--port', '8000'
    ], {
      cwd: pythonPath,
      env: {
        ...process.env,
        PYTHONPATH: pythonPathEnv,
        RENARDO_WEB_MODE: 'electron',
        RENARDO_STATIC_FOLDER: staticFolder
      }
    });
  } else {
    renardoPath = findRenardoPath();
    pythonPath = findPythonPath();
    staticFolder = findStaticFolder();

    console.log('Development mode');
    console.log('Renardo source path:', renardoPath);
    console.log('Python module path:', pythonPath);
    console.log('Static folder:', staticFolder);

    // Use uv to run uvicorn with proper environment
    serverProcess = spawn('uv', [
      'run', 'uvicorn',
      'renardo.webserver.app:app',
      '--host', '0.0.0.0',
      '--port', '8000',
      '--reload'
    ], {
      cwd: join(__dirname, '..', '..'),
      env: {
        ...process.env,
        RENARDO_WEB_MODE: 'electron',
        RENARDO_STATIC_FOLDER: staticFolder
      }
    });
  }

  console.log('Starting uvicorn server...');

  serverProcess.stdout.on('data', (data) => {
    console.log(`Server stdout: ${data.toString()}`);
  });

  serverProcess.stderr.on('data', (data) => {
    console.log(`Server stderr: ${data.toString()}`);
  });

  serverProcess.on('close', (code) => {
    console.log(`Server process exited with code ${code}`);
    serverProcess = null;
  });

  serverProcess.on('error', (error) => {
    console.error('Failed to start server process:', error);
    serverProcess = null;
  });

  console.log('Giving server time to start...');
  await new Promise(resolve => setTimeout(resolve, 3000));

  try {
    const result = await checkHealth();
    if (result) {
      console.log('Server confirmed ready!');
    } else {
      console.log('Server not responding to health check, but proceeding anyway...');
    }
  } catch (error) {
    console.log('Health check failed, but proceeding anyway...');
  }

  return true;
}

function checkHealth() {
  return new Promise((resolve) => {
    const req = http.get('http://localhost:8000/health', (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log('Health check successful:', data);
          resolve(true);
        } else {
          resolve(false);
        }
      });
    });

    req.on('error', () => resolve(false));
    req.setTimeout(2000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

function stopServer() {
  if (serverProcess) {
    console.log('Stopping server...');
    serverProcess.kill('SIGTERM');

    setTimeout(() => {
      if (serverProcess && !serverProcess.killed) {
        console.log('Force killing server process...');
        serverProcess.kill('SIGKILL');
      }
    }, 5000);

    serverProcess = null;
  }
}

function isServerRunning() {
  return serverProcess !== null && !serverProcess.killed;
}

export {
  startServer,
  stopServer,
  isServerRunning
};
