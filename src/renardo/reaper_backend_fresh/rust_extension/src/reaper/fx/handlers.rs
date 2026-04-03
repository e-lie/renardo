/*! REAPER FX OSC handlers */

use std::net::SocketAddr;
use rosc::{OscMessage, OscType};

use crate::reaper::api::*;
use crate::osc::send_response;

/// Handle OSC route: /fx/add (not used in fresh backend)
pub fn handle_add_fx(_msg: &OscMessage, _sender_addr: SocketAddr) {
    show_console_msg("[renardo-fresh] /fx/add not supported\n");
}

/// Handle OSC route: /fx/remove (not used in fresh backend)
pub fn handle_remove_fx(_msg: &OscMessage, _sender_addr: SocketAddr) {
    show_console_msg("[renardo-fresh] /fx/remove not supported\n");
}

/// Handle OSC route: /fx/param/get (not used — params are read at scan time)
pub fn handle_get_fx_param(_msg: &OscMessage, _sender_addr: SocketAddr) {
    show_console_msg("[renardo-fresh] /fx/param/get not supported — use /track/scan\n");
}

/// Handle OSC route: /fx/param/set
/// Expected args: [track_idx (int), fx_idx (int), param_idx (int), value (float, normalized 0.0-1.0)]
pub fn handle_set_fx_param(msg: &OscMessage, sender_addr: SocketAddr) {
    let track_idx = match msg.args.get(0) {
        Some(OscType::Int(v)) => *v,
        _ => { send_fx_error(sender_addr, "missing track_idx"); return; }
    };

    let fx_idx = match msg.args.get(1) {
        Some(OscType::Int(v)) => *v,
        _ => { send_fx_error(sender_addr, "missing fx_idx"); return; }
    };

    let param_idx = match msg.args.get(2) {
        Some(OscType::Int(v)) => *v,
        _ => { send_fx_error(sender_addr, "missing param_idx"); return; }
    };

    let value: f64 = match msg.args.get(3) {
        Some(OscType::Float(v)) => *v as f64,
        Some(OscType::Double(v)) => *v,
        Some(OscType::Int(v)) => *v as f64,
        _ => { send_fx_error(sender_addr, "missing value"); return; }
    };

    let value = value.clamp(0.0, 1.0);

    unsafe {
        let get_track = match GET_TRACK {
            Some(f) => f,
            None => { send_fx_error(sender_addr, "GET_TRACK unavailable"); return; }
        };
        let set_param = match TRACK_FX_SET_PARAM_NORMALIZED {
            Some(f) => f,
            None => { send_fx_error(sender_addr, "TrackFX_SetParamNormalized unavailable"); return; }
        };

        let track = get_track(std::ptr::null_mut(), track_idx);
        if track.is_null() {
            send_fx_error(sender_addr, "track not found");
            return;
        }

        let ok = set_param(track, fx_idx, param_idx, value);

        let response = OscMessage {
            addr: "/fx/param/set/response".to_string(),
            args: vec![
                OscType::Int(track_idx),
                OscType::Int(fx_idx),
                OscType::Int(param_idx),
                OscType::Float(value as f32),
                OscType::String(if ok { "success" } else { "error" }.to_string()),
            ],
        };
        send_response(response, sender_addr);
    }
}

fn send_fx_error(sender_addr: SocketAddr, error: &str) {
    show_console_msg(&format!("[renardo-fresh] /fx/param/set error: {}\n", error));
    let response = OscMessage {
        addr: "/fx/param/set/response".to_string(),
        args: vec![
            OscType::String("error".to_string()),
            OscType::String(error.to_string()),
        ],
    };
    send_response(response, sender_addr);
}
