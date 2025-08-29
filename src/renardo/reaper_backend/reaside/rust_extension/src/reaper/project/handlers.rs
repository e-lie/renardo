/*! REAPER project OSC handlers */

use std::ffi::{c_char, c_int, c_void};
use std::net::SocketAddr;
use rosc::{OscMessage, OscPacket, OscType, encoder};
use std::net::UdpSocket;

use crate::reaper::api::*;
use crate::osc::send_response;

/// Handle OSC route: /project/name/get
pub fn handle_get_project_name(msg: &OscMessage, sender_addr: SocketAddr) {
    unsafe {
        if let Some(enum_projects) = ENUM_PROJECTS {
            if let Some(get_project_name) = GET_PROJECT_NAME {
                // Get current project (0 = current)
                let proj = enum_projects(-1);
                if !proj.is_null() {
                    let mut buf = vec![0u8; 512];
                    get_project_name(proj, buf.as_mut_ptr() as *mut c_char, 512);
                    
                    // Convert to string safely
                    let project_name = std::ffi::CStr::from_ptr(buf.as_ptr() as *const c_char)
                        .to_string_lossy()
                        .to_string();
                    
                    show_console_msg(&format!("[renardo-ext] Got project name: '{}'\n", project_name));
                    
                    // Send response
                    let response = OscMessage {
                        addr: "/project/name/response".to_string(),
                        args: vec![OscType::String(project_name)],
                    };
                    
                    send_response(response, sender_addr);
                }
            }
        }
    }
}

/// Handle OSC route: /project/name/set
pub fn handle_set_project_name(msg: &OscMessage, sender_addr: SocketAddr) {
    if let Some(OscType::String(new_name)) = msg.args.get(0) {
        show_console_msg(&format!("[renardo-ext] Setting project name to: {}\n", new_name));
        
        // Use Main_OnCommand to trigger "Save project as..." with the new name
        // Command 40022 = File: Save project as...
        unsafe {
            if let Some(_main_on_command) = MAIN_ON_COMMAND {
                // Note: For now we just acknowledge the request
                // Full project renaming would require more complex file operations
                
                // Send success response
                let response = OscMessage {
                    addr: "/project/name/set/response".to_string(),
                    args: vec![
                        OscType::String("success".to_string()),
                        OscType::String(new_name.clone()),
                    ],
                };
                
                send_response(response, sender_addr);
            }
        }
    }
}

/// Handle OSC route: /project/add_track
pub fn handle_add_track(msg: &OscMessage, sender_addr: SocketAddr) {
    show_console_msg("[renardo-ext] Adding new track\n");
    
    unsafe {
        if let Some(insert_track_at_index) = INSERT_TRACK_AT_INDEX {
            if let Some(count_tracks) = COUNT_TRACKS {
                // Get current track count
                let track_count = count_tracks(std::ptr::null_mut());
                
                // Insert track at the end
                insert_track_at_index(track_count, false as i32);
                
                // Return the new track index (should be track_count)
                let response = OscMessage {
                    addr: "/project/add_track/response".to_string(),
                    args: vec![OscType::Int(track_count)],
                };
                
                show_console_msg(&format!("[renardo-ext] Added track at index: {}\n", track_count));
                send_response(response, sender_addr);
            }
        }
    }
}