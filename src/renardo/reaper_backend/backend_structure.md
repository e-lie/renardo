# REAPER Backend Structure Documentation

## Overview

The `reaper_backend` module provides comprehensive integration between Renardo and REAPER DAW, offering multiple approaches to control REAPER from Python code. The module is organized into several interconnected submodules that work together to provide a complete REAPER integration solution.

## Directory Structure

```
reaper_backend/
├── __init__.py                     # Main module exports
├── TODO.md                         # Module TODO documentation
├── reaper_music_resource.py        # REAPER-specific music resource classes
├── reaper_simple_lib.py            # Simple low-level REAPER utilities
├── ReaperIntegration/              # Higher-level integration layer
│   ├── __init__.py
│   └── ReaperInstruments.py
├── ReaperIntegrationLib/           # Advanced integration library
│   ├── __init__.py
│   ├── functions.py                # Utility functions
│   ├── ReaFX.py                    # Effect management classes
│   ├── ReaParam.py                 # Parameter management system
│   ├── ReaProject.py               # Core project management
│   ├── ReaTaskQueue.py             # Task scheduling and execution
│   ├── ReaTrack.py                 # Track representation and management
│   └── ReapyExtensions.py          # Reapy extensions
├── reaper_mgt/                     # REAPER instance management
│   ├── __init__.py
│   ├── launcher.py                 # Cross-platform REAPER launching
│   └── shared_library.py          # Python shared library detection
└── reaside/                        # Lua-based REAPER control system
    ├── __init__.py
    ├── config/                     # Configuration management
    │   ├── __init__.py
    │   ├── config.py
    │   └── resource_path.py
    ├── core/                       # Core REAPER operations
    │   ├── __init__.py
    │   ├── item.py                 # Media item operations
    │   ├── project.py              # Project-level operations
    │   ├── reaper.py               # Main REAPER interface
    │   ├── take.py                 # Take operations
    │   └── track.py                # Track-level operations
    ├── reascripts/                 # Lua scripts for REAPER
    │   └── reaside_server.lua
    └── tools/                      # Communication tools
        ├── __init__.py
        ├── reaper_client.py        # Unified HTTP/OSC client
        ├── reaper_http_client.py   # HTTP-based communication
        ├── reaper_osc_client.py    # OSC-based communication
        └── reaper_program.py       # REAPER program management
```

## Module Exports

Main exports from `__init__.py`:
- `ReaperInstrument`, `ReaperEffect` from `reaper_music_resource`
- `init_reapy_project` from `ReaperIntegration`
- `ensure_16_midi_tracks` from `reaper_simple_lib`

## Submodule Details

### 1. reaper_music_resource.py
**Purpose**: Implements REAPER-specific music resource classes for instruments and effects.

**Key Classes**:
- `ReaperEffect`: Represents REAPER effect processors with FX chain support
- `ReaperInstrument`: Main instrument class for REAPER integration with comprehensive functionality

**Key Features**:
- Automatic MIDI channel assignment (1-16)
- FX chain management and installation
- Parameter mapping between Renardo and REAPER
- Instrument proxy creation for Player integration
- Track management and preset handling
- Resource library integration for finding FX chains

### 2. reaper_simple_lib.py
**Purpose**: Provides simple, low-level utilities for basic REAPER operations using the `reapy` library.

**Key Functions**:
- Track management: `add_track()`, `rename_track()`, `get_track()`
- MIDI setup: `track_midi_input()`, `midi_selection_idx()`
- Volume control: `track_volume()`, `master_volume()`
- Send configuration: `add_send()`, `set_send_volume()`
- Standard track creation: `create_standard_midi_track()`, `ensure_16_midi_tracks()`

### 3. ReaperIntegration/
**Purpose**: Higher-level integration layer for REAPER project management.

**Key Components**:
- `__init__.py`: Contains `init_reapy_project()` function for project initialization
- `ReaperInstruments.py`: Empty file (functionality moved to `ReaperInstrument` class)

**Main Function**: `init_reapy_project(clock)` - Initializes a REAPER project with error handling

### 4. ReaperIntegrationLib/
**Purpose**: Advanced integration library providing object-oriented access to REAPER functionality.

**Key Components**:

#### ReaProject.py
Core project management class that:
- Manages tracks, effects, and project state
- Handles parameter mapping and updates
- Provides task queue for synchronized operations
- FX chain installation and management

#### ReaTrack.py
Track representation and management that:
- Encapsulates REAPER tracks with sends and effects
- Handles track parameters and FX management
- Supports both instrument and bus tracks

#### ReaFX.py
Effect management classes:
- `ReaFX`: Individual effect representation
- `ReaFXGroup`: Multiple effect instances management
- Parameter scanning and control

#### Other Components
- `ReaParam.py`: Parameter management system
- `ReaTaskQueue.py`: Task scheduling and execution
- `functions.py`: Utility functions for name conversion and parameter parsing

### 5. reaper_mgt/
**Purpose**: REAPER instance management and launcher utilities.

**Key Components**:

#### launcher.py
Cross-platform REAPER launching and configuration:
- `launch_reaper_with_pythonhome()`: Platform-specific REAPER launching
- `initialize_reapy()`: Reapy configuration and setup
- `reinit_reaper_with_backup()`: Configuration reset with backup
- `test_reaper_integration()`: Integration testing

#### shared_library.py
Python shared library detection utilities

### 6. reaside/
**Purpose**: Lua-based REAPER control system that doesn't require Python ReaScript API.

**Key Components**:

#### Core Module (core/)
- `reaper.py`: Main REAPER interface with transport control and project management
- `project.py`: Project-level operations
- `track.py`: Track-level operations
- `item.py`: Media item operations
- `take.py`: Take operations

#### Communication Tools (tools/)
- `reaper_client.py`: Unified HTTP/OSC client
- `reaper_http_client.py`: HTTP-based REAPER communication
- `reaper_osc_client.py`: OSC-based REAPER communication
- `reaper_program.py`: REAPER program management

#### Configuration (config/)
- `config.py`: Configuration management
- `resource_path.py`: Resource path detection

#### ReaScripts (reascripts/)
- `reaside_server.lua`: Lua script for REAPER-side API bridge

## Architecture Overview

The submodules work together in a layered architecture:

1. **Foundation Layer**: `reaper_simple_lib` provides basic reapy operations
2. **Integration Layer**: `ReaperIntegrationLib` provides object-oriented abstractions
3. **Resource Layer**: `reaper_music_resource` implements Renardo-specific instruments/effects
4. **Management Layer**: `reaper_mgt` handles REAPER instance lifecycle
5. **Alternative Layer**: `reaside` provides Lua-based control as an alternative to reapy

## Key Design Patterns

1. **Dual Integration Approach**: Both reapy-based (requiring Python ReaScript) and Lua-based (HTTP/OSC) integration
2. **Resource Management**: Automatic FX chain installation and management
3. **Parameter Mapping**: Comprehensive parameter translation between Renardo and REAPER
4. **Task Queue System**: Synchronized operations with REAPER's clock
5. **Cross-Platform Support**: Full Windows, macOS, and Linux compatibility

## Integration Relationships

The module provides a complete solution for REAPER integration, from simple track operations to complex instrument management and real-time parameter control. The different approaches allow for flexible integration depending on the user's REAPER configuration and requirements.

### Reapy-based Integration
Uses Python ReaScript API for direct REAPER control. Requires REAPER to be configured with Python ReaScript support.

### Reaside Integration
Uses Lua scripts and HTTP/OSC communication for REAPER control. Doesn't require Python ReaScript configuration and works across all platforms.

## Related Files

- `/src/renardo/test_reaper_integration.py`: Integration testing
- Other backend modules: `midi_backend`, `sc_backend`