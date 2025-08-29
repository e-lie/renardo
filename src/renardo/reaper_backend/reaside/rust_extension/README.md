# Renardo REAPER Extension

A native Rust REAPER extension providing OSC-based control interface for the Renardo live coding environment.

## Architecture

The extension is organized into a modular structure for scalability:

```
src/
├── lib.rs              # Main entry point and plugin initialization
├── reaper/             # REAPER API bindings and handlers
│   ├── mod.rs          # Module exports
│   ├── api.rs          # Core REAPER API function pointers and utilities
│   ├── project/        # Project-level operations
│   │   ├── mod.rs      
│   │   └── handlers.rs # OSC handlers for project operations
│   ├── track/          # Track-level operations  
│   │   ├── mod.rs
│   │   └── handlers.rs # OSC handlers for track operations
│   └── fx/             # FX-level operations (planned)
│       ├── mod.rs
│       └── handlers.rs # OSC handlers for FX operations
└── osc/                # OSC server and message routing
    ├── mod.rs          # Module exports
    ├── server.rs       # UDP server implementation
    ├── router.rs       # Message routing and dispatch
    └── utils.rs        # OSC utilities and response handling
```

## OSC Interface

The extension provides bidirectional OSC communication:
- **Listen Port**: 9877 (receives commands from Python)
- **Send Port**: 9878 (sends responses to Python)

### Available Routes

#### Project Operations
- `/project/name/get` - Get current project name
- `/project/name/set <name>` - Set project name
- `/project/add_track` - Add new track to project

#### Track Operations  
- `/track/name/get <track_index>` - Get track name by index
- `/track/name/set <track_index> <name>` - Set track name by index

#### FX Operations (Planned)
- `/fx/add <track_index> <fx_name>` - Add FX to track
- `/fx/remove <track_index> <fx_index>` - Remove FX from track
- `/fx/param/get <track_index> <fx_index> <param_index>` - Get FX parameter
- `/fx/param/set <track_index> <fx_index> <param_index> <value>` - Set FX parameter

## Building

```bash
cargo build --release
```

The compiled extension will be at `target/release/librenardo_reaper_ext.so` (Linux) or `target/release/renardo_reaper_ext.dll` (Windows).

## Installation

The extension is automatically installed by the Python configuration system:

```python
from src.renardo.reaper_backend.reaside import configure_reaper
configure_reaper()
```

This will:
1. Stop REAPER if running
2. Build and install the Rust extension 
3. Configure Lua ReaScript
4. Restart REAPER with the extension loaded

## Development

### Adding New Handlers

1. **Create handler function** in appropriate module (e.g., `reaper/track/handlers.rs`):
```rust
pub fn handle_new_operation(msg: &OscMessage, sender_addr: SocketAddr) {
    // Implementation here
    let response = OscMessage { /* ... */ };
    send_response(response, sender_addr);
}
```

2. **Add route** in `osc/router.rs`:
```rust
"/track/new_operation" => handle_new_operation(&msg, sender_addr),
```

3. **Export function** in appropriate `mod.rs` file

### Architecture Benefits

- **Modularity**: Easy to add new functionality without modifying core files
- **Separation of Concerns**: OSC handling separated from REAPER API logic  
- **Scalability**: Can grow to support hundreds of routes without becoming unwieldy
- **Maintainability**: Small focused files are easier to understand and modify
- **Testability**: Individual modules can be tested in isolation

## Integration with Python

The extension integrates seamlessly with the existing reaside Python API:

```python
# Add track via Rust OSC
new_track = project.basic_add_track()

# Set track name via Rust OSC  
new_track.name = "My Track"

# Get track name via Rust OSC
track_name = new_track.name
```

All operations transparently use the native Rust extension for optimal performance.