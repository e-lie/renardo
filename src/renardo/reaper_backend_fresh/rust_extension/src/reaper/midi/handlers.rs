/*! REAPER MIDI OSC handlers */

use std::net::SocketAddr;
use std::ffi::CString;
use rosc::{OscMessage, OscType};

use crate::reaper::api::*;
use crate::osc::send_response;
use super::note_manager::get_note_manager;

/// Handle OSC route: /note
/// Expected args: [midi_channel (int), midi_note (int), velocity (int), duration_ms (int)]
pub fn handle_play_note(msg: &OscMessage, sender_addr: SocketAddr) {
    // Parse arguments
    let midi_channel = msg.args.get(0)
        .and_then(|arg| if let OscType::Int(ch) = arg { Some(*ch as u8) } else { None })
        .unwrap_or(1);
    
    let midi_note = msg.args.get(1)
        .and_then(|arg| if let OscType::Int(note) = arg { Some(*note as u8) } else { None })
        .unwrap_or(60); // Default to middle C
    
    let velocity = msg.args.get(2)
        .and_then(|arg| if let OscType::Int(vel) = arg { Some(*vel as u8) } else { None })
        .unwrap_or(100);
    
    let duration_ms = msg.args.get(3)
        .and_then(|arg| if let OscType::Int(dur) = arg { Some(*dur as u64) } else { None })
        .unwrap_or(1000);

    if midi_channel < 1 || midi_channel > 16 {
        show_console_msg(&format!("[renardo-ext] Error: invalid MIDI channel {}, must be 1-16\n", midi_channel));
        
        // Send error response
        let response = OscMessage {
            addr: "/note/response".to_string(),
            args: vec![
                OscType::String("error".to_string()),
                OscType::String(format!("Invalid MIDI channel {}", midi_channel)),
            ],
        };
        send_response(response, sender_addr);
        return;
    }

    show_console_msg(&format!(
        "[renardo-ext] Note request: ch={}, note={}, vel={}, dur={}ms\n", 
        midi_channel, midi_note, velocity, duration_ms
    ));

    // Use the note manager to play the note
    let manager = get_note_manager();
    if let Ok(mut note_manager) = manager.lock() {
        note_manager.play_note(
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
            OscType::Int(midi_channel as i32),
            OscType::Int(midi_note as i32),
            OscType::Int(velocity as i32),
            OscType::Int(duration_ms as i32),
        ],
    };
    send_response(response, sender_addr);
}

