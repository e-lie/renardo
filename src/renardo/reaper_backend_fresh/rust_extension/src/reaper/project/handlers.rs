/*! REAPER project OSC handlers — fresh backend */

use std::ffi::{c_char, c_void};
use std::net::SocketAddr;
use rosc::{OscMessage, OscType};

use crate::reaper::api::*;
use crate::osc::send_response;

/// Handle OSC route: /project/track_count
pub fn handle_track_count(_msg: &OscMessage, sender_addr: SocketAddr) {
    unsafe {
        let count = COUNT_TRACKS.map(|f| f(std::ptr::null_mut())).unwrap_or(0);
        let response = OscMessage {
            addr: "/project/track_count/response".to_string(),
            args: vec![OscType::Int(count)],
        };
        send_response(response, sender_addr);
    }
}

/// Handle OSC route: /project/tempo/get
pub fn handle_get_tempo(_msg: &OscMessage, sender_addr: SocketAddr) {
    unsafe {
        let bpm = MASTER_GET_TEMPO.map(|f| f()).unwrap_or(120.0);
        let response = OscMessage {
            addr: "/project/tempo/get/response".to_string(),
            args: vec![OscType::Float(bpm as f32)],
        };
        send_response(response, sender_addr);
    }
}

/// Handle OSC route: /project/tempo/set
/// Expected args: [bpm (float)]
pub fn handle_set_tempo(msg: &OscMessage, sender_addr: SocketAddr) {
    let bpm: f64 = match msg.args.get(0) {
        Some(OscType::Float(v)) => *v as f64,
        Some(OscType::Double(v)) => *v,
        Some(OscType::Int(v)) => *v as f64,
        _ => {
            let response = OscMessage {
                addr: "/project/tempo/set/response".to_string(),
                args: vec![
                    OscType::String("error".to_string()),
                    OscType::String("missing bpm argument".to_string()),
                ],
            };
            send_response(response, sender_addr);
            return;
        }
    };

    let bpm = bpm.clamp(20.0, 999.0);

    unsafe {
        if let Some(set_bpm) = SET_CURRENT_BPM {
            set_bpm(std::ptr::null_mut(), bpm, false);
            let response = OscMessage {
                addr: "/project/tempo/set/response".to_string(),
                args: vec![
                    OscType::Float(bpm as f32),
                    OscType::String("success".to_string()),
                ],
            };
            send_response(response, sender_addr);
        } else {
            show_console_msg("[renardo-fresh] SetCurrentBPM unavailable\n");
            let response = OscMessage {
                addr: "/project/tempo/set/response".to_string(),
                args: vec![
                    OscType::String("error".to_string()),
                    OscType::String("SetCurrentBPM unavailable".to_string()),
                ],
            };
            send_response(response, sender_addr);
        }
    }
}
