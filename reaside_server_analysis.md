# ReaSide Server Lua Analysis

## Overview
The `reaside_server.lua` script provides a bridge between Python and REAPER's ReaScript API via ExtState communication. It runs continuously in REAPER and processes requests from Python clients.

## Core Capabilities

### 1. **Track Scanning** (`scan_track_complete()`)
- **Purpose**: Complete deep scan of track information including FX and parameters
- **Trigger**: ExtState key `"scan_track_request"` with track index
- **Python Integration**: 
  - `src/renardo/reaper_backend/reaside/core/track.py` → `ReaTrack.__init__()` 
  - `src/renardo/reaper_backend/reaside/client.py` → `Client.call_reascript_function()`

**Collected Data:**
- Basic track info (name, index)
- Track state (volume, pan, mute, solo, record arm)
- MIDI input configuration (`I_RECINPUT`, `I_RECMODE`, `I_RECMON`)
- Track color
- Complete FX chain information:
  - FX name, enabled status, preset
  - All parameter names, values, ranges, formatted values
- Send information:
  - Destination tracks, volume, pan, mute, phase, mono settings

### 2. **FX Chain Management**

#### **Save FX Chain** (`save_fxchain()`)
- **Purpose**: Extract FX chain from track and save as `.RfxChain` file
- **Trigger**: ExtState key `"save_fxchain_request"` with JSON: `{"track_index": 0, "file_path": "/path/file.RfxChain"}`
- **Python Integration**: 
  - `src/renardo/reaper_backend/reaside/core/fx.py` → `ReaFX.save_fx_chain()`
  - Uses track state chunk parsing to extract `<FXCHAIN>` section

**Process:**
1. Gets track state chunk via `GetTrackStateChunk()`
2. Parses XML to extract `<FXCHAIN>` section
3. Removes outer tags and saves inner content to file
4. Handles nested XML structure with depth counting

#### **Add FX Chain** (`add_fxchain()`)
- **Purpose**: Load FX chain from `.RfxChain` file and add to track
- **Trigger**: ExtState key `"add_fxchain_request"` with JSON: `{"track_index": 0, "file_path": "/path/file.RfxChain"}`
- **Python Integration**: 
  - `src/renardo/reaper_backend/reaside/core/fx.py` → `ReaFX.load_fx_chain()`

**Advanced Process (ReaperIntegrationLib approach):**
1. Creates temporary track
2. Adds FX chain content to temp track via `SetTrackStateChunk()`
3. Moves FX from temp track to target track using `TrackFX_CopyToTrack()`
4. Deletes temporary track
5. Prevents UI refresh during operation for performance

### 3. **Generic ReaScript Function Execution** (`execute_function()`)
- **Purpose**: Execute any REAPER ReaScript API function with arguments
- **Trigger**: ExtState key `"function_call"` with JSON: `{"function": "FuncName", "args": [arg1, arg2, ...]}`
- **Python Integration**: 
  - `src/renardo/reaper_backend/reaside/client.py` → `Client.call_reascript_function()`
  - **This is the primary interface used by ALL Python reaside operations**

**Advanced Features:**
- **Pointer Management**: Stores `userdata` objects (MediaTrack, MediaItem) in cache with string IDs
- **Multi-value Returns**: Captures all return values from functions
- **Type Conversion**: Handles strings, numbers, booleans, null values
- **Complex Argument Parsing**: Supports nested JSON structures, quoted strings, arrays

## Utility Functions

### 4. **JSON Processing**
- `parse_json()` - Simple JSON parser for ExtState values
- `to_json()` - Converts Lua values to JSON format
- Handles arrays, objects, type detection

### 5. **ExtState Management**
- `get_ext_state()` / `set_ext_state()` - ExtState read/write with JSON support
- **Section**: `"reaside"` - All operations use this ExtState section

### 6. **Pointer Cache System**
- `store_pointer()` / `get_pointer()` - Cache system for REAPER userdata objects
- Allows Python to reference REAPER objects across multiple function calls
- Uses format `"PTR_1"`, `"PTR_2"` etc.

### 7. **Error Handling & Logging**
- Debug logging to REAPER console when `DEBUG = true`
- Error responses via ExtState with `{"error": "message"}` format
- Request cleanup to prevent repeated execution

## Python Integration Points

### **Core Files Using reaside_server.lua:**

1. **`src/renardo/reaper_backend/reaside/client.py`**
   - `Client.call_reascript_function()` - **Primary interface**
   - Used by ALL reaside operations (tracks, FX, items, etc.)

2. **`src/renardo/reaper_backend/reaside/core/track.py`**
   - `ReaTrack.__init__()` - Calls track scanning
   - `ReaTrack.volume`, `ReaTrack.pan` - Uses generic function calls  
   - `ReaTrack.add_send()` - Track routing operations

3. **`src/renardo/reaper_backend/reaside/core/fx.py`**
   - `ReaFX` class - FX parameter manipulation
   - FX chain save/load operations
   - Parameter automation

4. **`src/renardo/reaper_backend/reaside/core/item.py`**
   - `ReaItem` - Media item manipulation
   - Uses generic ReaScript calls for item properties

5. **`src/renardo/reaper_backend/reaside/core/project.py`**
   - `ReaProject` - Project-level operations
   - Track creation, project properties

### **Key Integration Pattern:**
```python
# Python side
client.call_reascript_function("GetTrack", 0, track_index)

# Lua side receives:
{
  "function": "GetTrack", 
  "args": [0, track_index]
}

# Lua executes and stores result:
{
  "success": true,
  "result": ["PTR_123"]  # Pointer ID for userdata
}
```

## Server Lifecycle

### **Initialization:**
1. Sets ExtState values: `"api_status"`, `"version"`, `"last_updated"`
2. Attempts to determine script action ID for external triggering
3. Sets instance lock to prevent multiple instances

### **Main Loop:**
- Runs via `reaper.defer(run_main_loop)` for continuous polling
- Checks for pending requests every loop iteration
- Updates timestamp to indicate activity

### **Cleanup:**
- `onexit()` handler clears ExtState values
- Removes instance lock and pending requests

## Performance Considerations

1. **UI Refresh Prevention**: Uses `reaper.PreventUIRefresh(1)` during FX operations
2. **Temporary Track Strategy**: Avoids direct chunk manipulation on target tracks
3. **Pointer Caching**: Reduces overhead of recreating userdata objects
4. **Continuous Polling**: Low-overhead ExtState checking vs HTTP server

## Security & Reliability

1. **Instance Locking**: Prevents multiple server instances
2. **Request Cleanup**: Prevents command replay attacks
3. **Error Isolation**: Failed operations don't crash the server
4. **Type Safety**: Robust argument parsing and type checking

This server is the **backbone of all reaside operations** - every Python interaction with REAPER goes through this Lua bridge via the ExtState communication system.