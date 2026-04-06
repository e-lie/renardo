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

/// Handle OSC route: /fx/params/scan
/// Expected args: [track_idx (int), fx_idx (int), offset (int), count (int)]
/// Returns a paginated batch of FX parameter metadata.
/// Response: ["success", track_idx, fx_idx, offset, total_count, Blob]
/// Blob (serialize_osc_array): for each param — name, value, min, max, formatted
pub fn handle_scan_fx_params(msg: &OscMessage, sender_addr: SocketAddr) {
    let track_idx = match msg.args.get(0) {
        Some(OscType::Int(v)) => *v,
        _ => { send_fx_error(sender_addr, "missing track_idx"); return; }
    };
    let fx_idx = match msg.args.get(1) {
        Some(OscType::Int(v)) => *v,
        _ => { send_fx_error(sender_addr, "missing fx_idx"); return; }
    };
    let offset = match msg.args.get(2) {
        Some(OscType::Int(v)) => *v,
        _ => { send_fx_error(sender_addr, "missing offset"); return; }
    };
    let count = match msg.args.get(3) {
        Some(OscType::Int(v)) => *v,
        _ => { send_fx_error(sender_addr, "missing count"); return; }
    };

    use std::ffi::c_char;
    use crate::reaper::track::serialize_osc_array;

    unsafe {
        let get_track = match GET_TRACK {
            Some(f) => f,
            None => { send_fx_error(sender_addr, "GET_TRACK unavailable"); return; }
        };
        let track = get_track(std::ptr::null_mut(), track_idx);
        if track.is_null() {
            send_fx_error(sender_addr, "track not found");
            return;
        }

        let total_count = match TRACK_FX_GET_NUM_PARAMS {
            Some(f) => f(track, fx_idx),
            None => { send_fx_error(sender_addr, "TRACK_FX_GET_NUM_PARAMS unavailable"); return; }
        };

        let end = (offset + count).min(total_count);
        let mut param_data: Vec<OscType> = vec![];

        for param_idx in offset..end {
            // name
            let param_name = if let Some(get_name) = TRACK_FX_GET_PARAM_NAME {
                let mut buf = vec![0u8; 256];
                if get_name(track, fx_idx, param_idx, buf.as_mut_ptr() as *mut c_char, 256) {
                    std::ffi::CStr::from_ptr(buf.as_ptr() as *const c_char)
                        .to_string_lossy().to_string()
                } else {
                    format!("Param {}", param_idx)
                }
            } else { format!("Param {}", param_idx) };
            param_data.push(OscType::String(param_name));

            // value + min + max
            if let Some(get_param) = TRACK_FX_GET_PARAM {
                let mut min_val: f64 = 0.0;
                let mut max_val: f64 = 0.0;
                let value = get_param(track, fx_idx, param_idx, &mut min_val, &mut max_val);
                param_data.push(OscType::Float(value as f32));
                param_data.push(OscType::Float(min_val as f32));
                param_data.push(OscType::Float(max_val as f32));
            } else {
                param_data.push(OscType::Float(0.0));
                param_data.push(OscType::Float(0.0));
                param_data.push(OscType::Float(1.0));
            }

            // formatted value
            let formatted = if let Some(get_fmt) = TRACK_FX_GET_FORMATTED_PARAM_VALUE {
                let mut buf = vec![0u8; 256];
                if get_fmt(track, fx_idx, param_idx, buf.as_mut_ptr() as *mut c_char, 256) {
                    std::ffi::CStr::from_ptr(buf.as_ptr() as *const c_char)
                        .to_string_lossy().to_string()
                } else { "".to_string() }
            } else { "".to_string() };
            param_data.push(OscType::String(formatted));
        }

        let response = OscMessage {
            addr: "/fx/params/scan/response".to_string(),
            args: vec![
                OscType::String("success".to_string()),
                OscType::Int(track_idx),
                OscType::Int(fx_idx),
                OscType::Int(offset),
                OscType::Int(total_count),
                OscType::Blob(serialize_osc_array(&param_data)),
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
