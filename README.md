# Renardo

**Live coding environment for Python** - A modern fork of FoxDot for algorithmic music composition and live performance.

Renardo is currently going through a wide and deep refactoring toward version 1.0.

## Features

- **Live Coding**: Write and execute Python code in real-time to create music
- **Pattern-based Composition**: Powerful pattern system for rhythmic and melodic structures
- **Multiple Backends**:
  - SuperCollider integration for synthesis and audio processing
  - REAPER backend for advanced DAW integration
  - Ableton Live backend with Link synchronization
  - MIDI output support
- **Web-based Interface**: Modern, responsive web client built with Svelte
- **Desktop Application**: Optional Electron-based desktop app
- **Interactive Tutorials**: Built-in tutorials in multiple languages (English, Spanish)
- **Extensible**: Plugin system for custom instruments and effects
- **Resource Management**: Library system for managing samples, FX chains, and instruments

## Quick Start

### Prerequisites

- **Python** 3.9 or higher
- **SuperCollider** (for audio synthesis)
- **uv** (Python package manager) - recommended
- **REAPER** (optional, for REAPER DAW integration)
- **Ableton Live** (optional, for Ableton Live integration)

### Installation

#### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/renardo.git
cd renardo

# Install with uv
uv pip install -e .

# Or run directly with uv
uv run renardo
```

#### Using pip

```bash
pip install renardo
```

### First Run

```bash
# Launch Renardo with default settings
renardo

# Or use the CLI interface
uv run cli

# Interactive pipe mode
uv run cli --pipe
```

The web interface will automatically open at `http://localhost:5000`

## Usage

### Basic Live Coding Example

```python
# Create a simple drum pattern
d1 >> play("x-o-")

# Add a bassline
b1 >> bass([0, 3, 5, 7], dur=1/2)

# Modify in real-time
d1 >> play("x-o-", amp=1.2)

# Stop everything
Clock.clear()
```

### CLI Options

```bash
# Show all available commands
renardo --help
cli --help

# Start in pipe mode (for integration with other tools)
cli --pipe

# Launch with specific backend
renardo --backend supercollider
renardo --backend reaper
renardo --backend ableton

# Configure backend integration
renardo --configure-reaper
```

## Architecture

Renardo is organized into several key modules:

```
renardo/
├── lib/              # Core library (patterns, players, effects)
├── sc_backend/       # SuperCollider integration
├── reaper_backend/   # REAPER DAW integration
├── ableton_backend/  # Ableton Live integration
├── midi_backend/     # MIDI output support
├── webserver/        # Flask-based web server
├── runtime/          # Runtime environment and state management
├── settings_manager/ # Configuration management
├── gatherer/         # Resource library system
├── tutorial/         # Interactive tutorials (en, es)
└── cli_entrypoint/   # Command-line interface

webclient/
├── src/              # Svelte web interface
├── electron/         # Electron desktop app wrapper
└── dist/             # Built web assets
```

## Documentation

### Tutorials

Renardo includes interactive tutorials accessible from the web interface:

- **English**: `/tutorial/en/`
- **Spanish**: `/tutorial/es/`

Topics covered:
1. Introduction to live coding
2. Playing notes and samples
3. Algorithmic manipulation
4. Using patterns
5. Player attributes
6. Clock management
7. Advanced features (scales, groups, vars)
8. SuperCollider instruments
9. REAPER backend integration
10. Ableton Live backend integration

# Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feat/amazing-feature`)
3. **Commit** your changes using [Conventional Commits](https://www.conventionalcommits.org/)
   ```
   feat: add new pattern generator
   fix: resolve timing issue in Clock
   docs: update tutorial content
   ```
4. **Push** to your branch (`git push origin feat/amazing-feature`)
5. **Open** a Pull Request

We use Conventional Commits format


### Reference

Key components:

- **Players**: Objects that play patterns (`p1`, `d1`, `b1`, etc.)
- **Patterns**: Sequence generators (`P`, `PSum`, `PRand`, etc.)
- **Clock**: Global timing system
- **SynthDefs**: SuperCollider instrument definitions
- **TimeVars**: Variables that change over time

## Configuration

Renardo uses TOML files for configuration:

```bash
# Default config location
~/.renardo/settings.toml

# Backend settings (REAPER, Ableton, etc.)
~/.renardo/reaper_backend.toml
~/.renardo/ableton_backend.toml
```

### Example Configuration

```toml
[general]
backend = "supercollider"
auto_start = true

[supercollider]
port = 57120
audio_device = "default"

[reaper]
enabled = true
project_path = "~/Music/renardo_sessions"

[ableton_backend]
ABLETON_BACKEND_ENABLED = false
```

## Backends

### SuperCollider Backend

The default audio backend using SuperCollider for synthesis:

```python
# Start SuperCollider
from renardo.sc_backend import SuperColliderInstance

sc = SuperColliderInstance()
sc.start()

# Use SuperCollider instruments
p1 >> pluck([0, 2, 4, 7])
```

### REAPER Backend

Advanced DAW integration for professional production:

```python
# Initialize REAPER backend
from renardo.reaper_backend import ReaperBackend

reaper = ReaperBackend()
reaper.configure()

# Create REAPER instruments
r1 >> ReaperInstrument("my_synth.RfxChain", notes=[0, 4, 7])
```

### Ableton Live Backend

Deep integration with Ableton Live via pylive and Ableton Link:

```python
# Initialize Ableton backend
from renardo.ableton_backend import create_ableton_instruments

# Scan Live set and create instruments
instruments = create_ableton_instruments()
bass = instruments['Bass']
synth = instruments['Synth']

# Play notes and control parameters
p1 >> bass.out([0, 3, 7], dur=1/2, filter_cutoff=80)
p2 >> synth.out([7, 9, 12], reverb_mix=0.5)

# Trigger clips
p3 >> bass.out(clip=P[0, 1, 2], dur=4)

# Automate parameters with TimeVar (300Hz!)
p1 >> synth.out(degree=0, filter_cutoff=var([20, 127], 8))
```

Features:
- MIDI note output + OSC parameter control
- Clip triggering and scene launching
- TimeVar automation at 300Hz
- Ableton Link tempo synchronization (dual-threaded clock)
- Auto-discovery of tracks, devices, and parameters

See [docs/ableton_backend.md](docs/ableton_backend.md) for detailed documentation.

### MIDI Backend

Output to external MIDI devices:

```python
# Configure MIDI output
from renardo.midi_backend import MIDIOut

midi = MIDIOut("My MIDI Device")
m1 >> midi([60, 64, 67])  # C major chord
```

## Web Client

The web interface provides:

- **Code Editor**: Syntax highlighting, auto-completion
- **Console Output**: Real-time feedback
- **Session Management**: Save and load sessions
- **Settings Panel**: Configure backends and preferences
- **Tutorial Browser**: Access interactive tutorials
- **Resource Explorer**: Browse samples and instruments

### Development

```bash
cd webclient

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Build Electron app
npm run build:electron
```

## License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FoxDot**: Original live coding environment by Ryan Kirkbride
- **SuperCollider**: Synthesis engine
- **REAPER**: Digital Audio Workstation
- **Ableton Live**: Digital Audio Workstation
- **pylive** and **AbletonOSC**: Ableton Live OSC control
- All contributors to the Renardo project


## Contact & Community

- **Website**: [renardo.org](http://renardo.org/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/renardo/issues)
- **Discussions**: FoxDot / Renardo telegram channel


*Happy live coding! 🎵*
