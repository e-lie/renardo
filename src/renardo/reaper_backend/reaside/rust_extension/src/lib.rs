/*! Renardo REAPER Extension
 * 
 * A native Rust REAPER extension providing OSC-based control interface
 * for the Renardo live coding environment.
 * 
 * Architecture:
 * - `reaper/` - REAPER API bindings and handlers
 *   - `api.rs` - Core REAPER API function pointers
 *   - `project/` - Project-level operations
 *   - `track/` - Track-level operations  
 *   - `fx/` - FX-level operations
 * - `osc/` - OSC server and message routing
 *   - `server.rs` - UDP server implementation
 *   - `router.rs` - Message routing logic
 *   - `utils.rs` - OSC utilities
 */

use std::ffi::{c_char, c_int, c_void, CString};

mod reaper;
mod osc;

use reaper::api::{ReaperPluginInfo, initialize_api, show_console_msg};
use reaper::midi::{init_note_manager};
use osc::{OscServer, OSC_SERVER};

/// Plugin entry point called by REAPER
#[no_mangle]
pub extern "C" fn ReaperPluginEntry(
    _hinstance: *mut c_void,
    rec: *mut ReaperPluginInfo,
) -> c_int {
    if rec.is_null() {
        return 0;
    }
    
    unsafe {
        let plugin_info = &*rec;
        initialize_api(plugin_info);
    }
    
    // Initialize extension
    show_console_msg("=================================\n");
    show_console_msg("Renardo REAPER Extension loaded!\n");
    show_console_msg("=================================\n");
    
    // Initialize MIDI note manager
    init_note_manager();
    
    // Start OSC server on ports 9877 (receive) and 9878 (send)
    let server_port = 9877;
    let client_port = 9878;
    
    match OscServer::new(server_port, client_port) {
        Ok(server) => {
            show_console_msg(&format!("[renardo-ext] OSC server listening on port {}\n", server_port));
            show_console_msg(&format!("[renardo-ext] OSC client sending to port {}\n", client_port));
            show_console_msg("[renardo-ext] Available routes:\n");
            show_console_msg("  Project: /project/name/get, /project/name/set, /project/add_track\n");
            show_console_msg("  Track: /track/name/get, /track/name/set, /track/volume/*, /track/pan/*\n");
            show_console_msg("  MIDI: /note [track_name, note, velocity, duration_ms]\n");
            show_console_msg("  FX: /fx/* (planned)\n");
            
            // Store server in global state
            let mut server_guard = OSC_SERVER.lock();
            *server_guard = Some(server);
            
            show_console_msg("[renardo-ext] Extension ready!\n");
        }
        Err(e) => {
            show_console_msg(&format!("[renardo-ext] Failed to start OSC server: {}\n", e));
        }
    }
    
    1 // Success
}