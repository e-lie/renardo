# Renardo REAPER Extension

A native REAPER extension written in Rust that provides an OSC interface for controlling REAPER from Renardo.

## Features

- OSC server listening on port 9000
- `/demo/args` route for testing that logs all received parameters
- Extensible architecture for adding more OSC routes

## Building

### Prerequisites

1. Install Rust: https://rustup.rs/
2. Install REAPER (obviously)

### Build Steps

```bash
# Build the extension
./build.sh

# Or manually:
cargo build --release
```

## Installation

1. Build the extension (see above)
2. Copy the built library to your REAPER UserPlugins directory:
   - **Linux**: `~/.config/REAPER/UserPlugins/`
   - **macOS**: `~/Library/Application Support/REAPER/UserPlugins/`
   - **Windows**: `%APPDATA%\REAPER\UserPlugins\`

3. Rename the file:
   - **Linux**: Rename `librenardo_reaper_ext.so` to `reaper_renardo.so`
   - **macOS**: Rename `librenardo_reaper_ext.dylib` to `reaper_renardo.dylib`  
   - **Windows**: Rename `renardo_reaper_ext.dll` to `reaper_renardo.dll`

4. Restart REAPER

5. Check the REAPER console (View > Show REAPER Resource Path in Explorer/Finder) for the startup message:
   ```
   =================================
   Renardo REAPER Extension loaded!
   =================================
   [renardo-ext] OSC server started on port 9000
   ```

## Testing

Once installed, you can test the OSC interface:

### Using the test script:

```bash
# Install python-osc if needed
pip install python-osc

# Run the test script
python test_osc.py
```

### Manual testing with oscsend:

```bash
# Send a test message
oscsend localhost 9000 /demo/args ifs 42 3.14 "Hello"
```

### From Python:

```python
from pythonosc import udp_client

client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
client.send_message("/demo/args", [1, 2, 3, "test"])
```

## OSC Routes

Currently implemented:

- `/demo/args` - Logs all arguments received (for testing)

## Development

To add new OSC routes, edit `src/lib.rs` and add cases to the `match` statement in `handle_osc_message()`:

```rust
match msg.addr.as_str() {
    "/demo/args" => { /* existing handler */ }
    "/your/new/route" => {
        // Your handler code here
    }
    _ => { /* unknown route */ }
}
```

## Troubleshooting

1. **Extension not loading**: Check REAPER console for error messages
2. **Port already in use**: Another application is using port 9000
3. **No console output**: Make sure REAPER console is open (Actions > Show REAPER resource path)

## Architecture

The extension consists of:
- OSC server running in a separate thread
- Message handler that processes incoming OSC packets
- Integration with REAPER's console for logging
- Global state management for the server instance