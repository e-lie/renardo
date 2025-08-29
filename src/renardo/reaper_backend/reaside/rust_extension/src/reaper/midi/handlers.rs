/*! REAPER MIDI OSC handlers */

use std::net::SocketAddr;
use std::ffi::CString;
use rosc::{OscMessage, OscType};

use crate::reaper::api::*;
use crate::osc::send_response;
use super::note_manager::get_note_manager;

/// Handle OSC route: /note
/// Expected args: [track_name (string), midi_note (int), velocity (int), duration_ms (int)]
pub fn handle_play_note(msg: &OscMessage, sender_addr: SocketAddr) {
    // Parse arguments
    let track_name = msg.args.get(0)
        .and_then(|arg| if let OscType::String(name) = arg { Some(name.as_str()) } else { None })
        .unwrap_or("");
    
    let midi_note = msg.args.get(1)
        .and_then(|arg| if let OscType::Int(note) = arg { Some(*note as u8) } else { None })
        .unwrap_or(60); // Default to middle C
    
    let velocity = msg.args.get(2)
        .and_then(|arg| if let OscType::Int(vel) = arg { Some(*vel as u8) } else { None })
        .unwrap_or(100);
    
    let duration_ms = msg.args.get(3)
        .and_then(|arg| if let OscType::Int(dur) = arg { Some(*dur as u64) } else { None })
        .unwrap_or(1000);

    if track_name.is_empty() {
        show_console_msg("[renardo-ext] Error: track_name required for /note\n");
        return;
    }

    show_console_msg(&format!(
        "[renardo-ext] Note request: track='{}', note={}, vel={}, dur={}ms\n", 
        track_name, midi_note, velocity, duration_ms
    ));

    // Find the track and get its MIDI channel
    let midi_channel = match find_track_midi_channel(track_name) {
        Some(channel) => channel,
        None => {
            show_console_msg(&format!("[renardo-ext] Track '{}' not found or not configured for MIDI\n", track_name));
            
            // Send error response
            let response = OscMessage {
                addr: "/note/response".to_string(),
                args: vec![
                    OscType::String("error".to_string()),
                    OscType::String(format!("Track '{}' not found", track_name)),
                ],
            };
            send_response(response, sender_addr);
            return;
        }
    };

    // Use the note manager to play the note
    let manager = get_note_manager();
    if let Ok(mut note_manager) = manager.lock() {
        note_manager.play_note(
            track_name.to_string(),
            midi_channel,
            midi_note,
            velocity,
            duration_ms
        );
    }

    // Send success response
    let response = OscMessage {
        addr: "/note/response".to_string(),
        args: vec![
            OscType::String("success".to_string()),
            OscType::String(track_name.to_string()),
            OscType::Int(midi_note as i32),
            OscType::Int(velocity as i32),
            OscType::Int(duration_ms as i32),
        ],
    };
    send_response(response, sender_addr);
}

/// Find a track by name and return its MIDI channel
fn find_track_midi_channel(track_name: &str) -> Option<u8> {
    unsafe {
        if let Some(count_tracks) = COUNT_TRACKS {
            if let Some(get_track) = GET_TRACK {
                if let Some(get_track_name) = GET_TRACK_NAME {
                    if let Some(get_set_media_track_info) = GET_SET_MEDIA_TRACK_INFO {
                        
                        let track_count = count_tracks(std::ptr::null_mut());
                        
                        for track_idx in 0..track_count {
                            let track = get_track(std::ptr::null_mut(), track_idx);
                            if !track.is_null() {
                                // Get track name
                                let mut buf = vec![0u8; 256];
                                let success = get_track_name(track, buf.as_mut_ptr() as *mut i8, 256);
                                
                                if success {
                                    let current_track_name = std::ffi::CStr::from_ptr(buf.as_ptr() as *const i8)
                                        .to_string_lossy()
                                        .to_string();
                                    
                                    if current_track_name == track_name {
                                        // Get MIDI input configuration
                                        let param_name = CString::new("I_RECINPUT").unwrap();
                                        let mut midi_input: i32 = 0;
                                        
                                        get_set_media_track_info(
                                            track,
                                            param_name.as_ptr(),
                                            &mut midi_input as *mut i32 as *mut std::ffi::c_void,
                                            0 // setNewValue = false (get)
                                        );
                                        
                                        // Check if it's a MIDI track (has MIDI input configured)
                                        if midi_input >= 4096 {
                                            // Extract MIDI channel from the input value
                                            // Low 5 bits are the channel (0=all, 1-16=specific)
                                            let midi_channel = (midi_input & 0x1F) as u8;
                                            if midi_channel >= 1 && midi_channel <= 16 {
                                                show_console_msg(&format!(
                                                    "[renardo-ext] Found track '{}' at index {} with MIDI channel {}\n", 
                                                    track_name, track_idx, midi_channel
                                                ));
                                                return Some(midi_channel - 1); // Convert to 0-based for MIDI messages
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    None
}