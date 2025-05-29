# Installation Guide

This guide will walk you through the process of installing Renardo and its dependencies.

## Prerequisites

Renardo requires:

- Python 3.9 or higher
- SuperCollider (for sound synthesis)
- Additional Python packages (installed automatically with Renardo)

## Installing Renardo

### Using pip

The simplest way to install Renardo is using pip:

```bash
pip install renardo
```

This will install Renardo and all its required Python dependencies.

### From Source

To install the latest development version:

1. Clone the repository:
   ```bash
   git clone https://github.com/Bubobubobubobubo/Renardo.git
   ```

2. Navigate to the directory:
   ```bash
   cd Renardo
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Installing SuperCollider

Renardo uses SuperCollider for sound generation. If you don't already have SuperCollider installed, follow these instructions:

### Windows

1. Download the installer from [SuperCollider's website](https://supercollider.github.io/download)
2. Run the installer and follow the prompts
3. Make sure the SC3 plugins option is selected during installation

### macOS

1. Download the macOS app from [SuperCollider's website](https://supercollider.github.io/download)
2. Move the SuperCollider app to your Applications folder
3. Install the SC3 plugins by downloading them from the same page

### Linux

#### Ubuntu/Debian
```bash
sudo apt-get install supercollider sc3-plugins
```

#### Arch Linux
```bash
sudo pacman -S supercollider sc3-plugins
```

#### Fedora
```bash
sudo dnf install supercollider sc3-plugins
```

## First Launch

After installing Renardo, you can launch it by running:

```bash
renardo
```

On first launch, Renardo will:

1. Check for SuperCollider installation
2. Create a user directory for your files
3. Download default sample packs
4. Initialize the SuperCollider server

## Troubleshooting

### SuperCollider Not Found

If Renardo can't find your SuperCollider installation:

1. Open Renardo
2. Click on Settings > Preferences
3. In the "SuperCollider" tab, set the path to your SuperCollider executable

### Sound Issues

If you're not hearing any sound:

1. Make sure your system's audio is working
2. Check that SuperCollider is properly installed
3. Restart Renardo and make sure the initialization is complete

### Sample Packs Not Available

If you're missing sample packs:

1. Go to Settings > Sample Packs
2. Click "Download Default Samples"

## Next Steps

Once you have Renardo installed:

- Check out the [Tutorials](./tutorials.md) to learn the basics
- Explore the [Editor Guide](./editor/index.md) to understand the interface
- Try the included examples to hear what Renardo can do