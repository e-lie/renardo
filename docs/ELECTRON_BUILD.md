# Building Renardo Electron Application

This guide explains how to build the Renardo Electron application for desktop deployment.

## Prerequisites

1. Node.js and npm installed
2. Python 3.9+ for running the install script

## Setup Steps

### 1. Install Python Standalone Distribution

Before building the Electron app, you need to download the Python standalone distribution for your platform:

```bash
# From the project root directory
python install_standalone_python.py
```

This script will:
- Detect your OS and architecture (Windows/macOS/Linux, x64/arm64)
- Download the appropriate Python 3.12.7 standalone distribution
- Extract it to `webclient/python/`
- Configure it for use with the Electron build

**Note**: The `webclient/python/` directory is excluded from git as it contains large binary files.

### 2. Build the Web Client

```bash
cd webclient
npm install
npm run build
```

### 3. Build the Electron Application

#### For the current platform:
```bash
npm run build:electron
```

#### For specific platforms:
```bash
# Windows
npx electron-builder --win

# macOS
npx electron-builder --mac

# Linux AppImage
npx electron-builder --linux AppImage

# Linux deb
npx electron-builder --linux deb
```

## Output

Built applications will be in `webclient/dist-electron/`:
- **Windows**: `Renardo-*.exe` (installer)
- **macOS**: `Renardo-*.dmg`
- **Linux**: `Renardo-*.AppImage` and `renardo_*.deb`

## Architecture Support

The install script supports:
- **Linux**: x64, arm64
- **macOS**: x64 (Intel), arm64 (Apple Silicon)
- **Windows**: x64, x86

## How It Works

1. **Standalone Python**: The Electron app bundles a complete Python runtime, making it work without Python installed on the user's machine.

2. **Dependencies**: On first run, the app installs required Python packages to a temporary directory (`/tmp/renardo-electron/site-packages` on Unix, `%TEMP%\renardo-electron\site-packages` on Windows).

3. **Flask Server**: The embedded Python runs the Renardo Flask server, which serves the web interface.

4. **Electron Wrapper**: Electron provides the desktop window and loads the Flask-served web interface.

## Troubleshooting

### Python Download Issues
If the download fails, you can manually download from:
https://github.com/indygreg/python-build-standalone/releases

Look for files named like:
- `cpython-3.12.7+20241016-{arch}-{platform}-install_only.tar.gz`

Extract to `webclient/python/`.

### Build Errors
- Ensure all dependencies are installed: `npm install`
- Clear the build cache: `rm -rf dist-electron/`
- Check that `webclient/dist/` exists (run `npm run build` first)

### Runtime Errors
- Check the console output in development mode: `npm run dev:electron`
- Look for Flask server errors in the Electron console
- Verify Python dependencies are installing correctly