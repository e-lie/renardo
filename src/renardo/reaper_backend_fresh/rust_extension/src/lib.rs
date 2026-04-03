/*! Renardo REAPER Fresh Extension
 *
 * Plugin natif REAPER OSC — backend fresh (scan-only, pas de création de tracks).
 * Routes : /project/track_count, /project/tempo/get|set,
 *           /track/scan, /track/volume|pan/get|set,
 *           /fx/param/set,
 *           /note
 */

use std::ffi::{c_int, c_void};

mod reaper;
mod osc;

use reaper::api::{ReaperPluginInfo, initialize_api, show_console_msg};
use reaper::midi::init_note_manager;
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

    show_console_msg("=====================================\n");
    show_console_msg("Renardo REAPER Fresh Extension loaded\n");
    show_console_msg("=====================================\n");

    init_note_manager();

    let server_port = 9877u16;
    let client_port = 9878u16;

    match OscServer::new(server_port, client_port) {
        Ok(server) => {
            show_console_msg(&format!("[renardo-fresh] OSC listening on port {}\n", server_port));
            show_console_msg("[renardo-fresh] Routes:\n");
            show_console_msg("  /project/track_count\n");
            show_console_msg("  /project/tempo/get|set <bpm>\n");
            show_console_msg("  /track/scan <idx>\n");
            show_console_msg("  /track/volume|pan/get|set <idx> [value]\n");
            show_console_msg("  /fx/param/set <track_idx> <fx_idx> <param_idx> <value 0-1>\n");
            show_console_msg("  /note <channel> <note> <velocity> <duration_ms>\n");

            let mut server_guard = OSC_SERVER.lock();
            *server_guard = Some(server);

            show_console_msg("[renardo-fresh] Ready!\n");
        }
        Err(e) => {
            show_console_msg(&format!("[renardo-fresh] Failed to start OSC server: {}\n", e));
        }
    }

    1
}
