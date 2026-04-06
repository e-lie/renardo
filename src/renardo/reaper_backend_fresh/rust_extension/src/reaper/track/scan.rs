/*! Complete track scanning with FX and sends */

use std::net::SocketAddr;
use std::ffi::{c_char, c_void, CString};
use rosc::{OscMessage, OscType};

use crate::reaper::api::*;
use crate::osc::send_response;

/// Handle OSC route: /track/scan
/// Expected args: [track_index (int)]
/// Returns complete track information including FX and sends
pub fn handle_scan_track(msg: &OscMessage, sender_addr: SocketAddr) {
    let track_index = msg.args.get(0)
        .and_then(|arg| if let OscType::Int(idx) = arg { Some(*idx) } else { None })
        .unwrap_or(-1);
    
    if track_index < 0 {
        send_error_response(sender_addr, "Invalid track index");
        return;
    }
    
    show_console_msg(&format!("[renardo-ext] Scanning track at index {}\n", track_index));
    
    unsafe {
        // Get track
        if let Some(get_track) = GET_TRACK {
            let track = get_track(std::ptr::null_mut(), track_index);
            if track.is_null() {
                send_error_response(sender_addr, "Track not found");
                return;
            }
            
            // Collect track data
            let mut response_args = vec![
                OscType::String("success".to_string()),
                OscType::Int(track_index),
            ];
            
            // Basic track info
            if let Some(get_track_name) = GET_TRACK_NAME {
                let mut name_buf = vec![0u8; 256];
                let success = get_track_name(track, name_buf.as_mut_ptr() as *mut c_char, 256);
                if success {
                    let name = std::ffi::CStr::from_ptr(name_buf.as_ptr() as *const c_char)
                        .to_string_lossy()
                        .to_string();
                    response_args.push(OscType::String(name));
                } else {
                    response_args.push(OscType::String("".to_string()));
                }
            }
            
            // Track properties — use GetMediaTrackInfo_Value (read-only, returns f64)
            // NOTE: GET_SET_MEDIA_TRACK_INFO must NOT be used for reads here because our
            // Rust declaration has a wrong 4th arg; the real REAPER API takes only 3 args
            // and treats any non-NULL 3rd arg as a SET operation, corrupting project state.
            if let Some(get_val) = GET_MEDIA_TRACK_INFO_VALUE {
                let param_d_vol    = CString::new("D_VOL").unwrap();
                let param_d_pan    = CString::new("D_PAN").unwrap();
                let param_b_mute   = CString::new("B_MUTE").unwrap();
                let param_i_solo   = CString::new("I_SOLO").unwrap();
                let param_i_recarm = CString::new("I_RECARM").unwrap();
                let param_i_recinput = CString::new("I_RECINPUT").unwrap();
                let param_i_recmode  = CString::new("I_RECMODE").unwrap();
                let param_i_recmon   = CString::new("I_RECMON").unwrap();

                let volume   = get_val(track, param_d_vol.as_ptr());
                let pan      = get_val(track, param_d_pan.as_ptr());
                let mute     = get_val(track, param_b_mute.as_ptr());
                let solo     = get_val(track, param_i_solo.as_ptr());
                let rec_arm  = get_val(track, param_i_recarm.as_ptr());
                let rec_input = get_val(track, param_i_recinput.as_ptr());
                let rec_mode  = get_val(track, param_i_recmode.as_ptr());
                let rec_mon   = get_val(track, param_i_recmon.as_ptr());

                response_args.push(OscType::Float(volume as f32));
                response_args.push(OscType::Float(pan as f32));
                response_args.push(OscType::Bool(mute > 0.0));
                response_args.push(OscType::Bool(solo > 0.0));
                response_args.push(OscType::Bool(rec_arm > 0.0));
                response_args.push(OscType::Int(rec_input as i32));
                response_args.push(OscType::Int(rec_mode as i32));
                response_args.push(OscType::Int(rec_mon as i32));
            }
            
            // Track color
            if let Some(get_color) = GET_TRACK_COLOR {
                let color = get_color(track);
                response_args.push(OscType::Int(color));
            } else {
                response_args.push(OscType::Int(0));
            }
            
            // FX information — metadata only (no param values, use /fx/params/scan for those)
            let mut fx_data = vec![];
            if let Some(fx_count_fn) = TRACK_FX_GET_COUNT {
                let fx_count = fx_count_fn(track);
                // Note: fx_count is NOT pushed to fx_data — Python parses FX entries until blob ends

                show_console_msg(&format!("[renardo-ext] Track has {} FX\n", fx_count));

                for fx_idx in 0..fx_count {
                    // FX name
                    if let Some(get_fx_name) = TRACK_FX_GET_FX_NAME {
                        let mut name_buf = vec![0u8; 256];
                        let success = get_fx_name(track, fx_idx, name_buf.as_mut_ptr() as *mut c_char, 256);
                        if success {
                            let fx_name = std::ffi::CStr::from_ptr(name_buf.as_ptr() as *const c_char)
                                .to_string_lossy()
                                .to_string();
                            fx_data.push(OscType::String(fx_name));
                        } else {
                            fx_data.push(OscType::String("Unknown".to_string()));
                        }
                    }

                    // FX enabled
                    if let Some(get_enabled) = TRACK_FX_GET_ENABLED {
                        let enabled = get_enabled(track, fx_idx);
                        fx_data.push(OscType::Bool(enabled));
                    } else {
                        fx_data.push(OscType::Bool(true));
                    }

                    // FX preset
                    if let Some(get_preset) = TRACK_FX_GET_PRESET {
                        let mut preset_buf = vec![0u8; 256];
                        let success = get_preset(track, fx_idx, preset_buf.as_mut_ptr() as *mut c_char, 256);
                        if success {
                            let preset_name = std::ffi::CStr::from_ptr(preset_buf.as_ptr() as *const c_char)
                                .to_string_lossy()
                                .to_string();
                            fx_data.push(OscType::String(preset_name));
                        } else {
                            fx_data.push(OscType::String("".to_string()));
                        }
                    }

                    // Parameter count only — actual param values fetched via /fx/params/scan
                    if let Some(get_param_count) = TRACK_FX_GET_NUM_PARAMS {
                        let param_count = get_param_count(track, fx_idx);
                        fx_data.push(OscType::Int(param_count));
                    } else {
                        fx_data.push(OscType::Int(0));
                    }
                }
            }
            
            // Add FX data as blob
            response_args.push(OscType::Blob(serialize_osc_array(&fx_data)));
            
            // Send information
            let mut send_data = vec![];
            if let Some(get_send_count) = GET_TRACK_NUM_SENDS {
                let send_count = get_send_count(track, 0); // 0 = sends (not receives or hardware)
                send_data.push(OscType::Int(send_count));
                
                show_console_msg(&format!("[renardo-ext] Track has {} sends\n", send_count));
                
                for send_idx in 0..send_count {
                    // Get destination track
                    if let Some(get_send_info) = GET_TRACK_SEND_INFO_VALUE {
                        // Get destination track pointer - this is a special case where the double contains a pointer
                        let param = CString::new("P_DESTTRACK").unwrap();
                        let dest_track_value = get_send_info(track, 0, send_idx, param.as_ptr());
                        // Convert the double to pointer (REAPER stores pointers as doubles for this parameter)
                        let dest_track_ptr = (dest_track_value as usize) as *mut c_void;
                        
                        if !dest_track_ptr.is_null() {
                            // Get destination track name
                            if let Some(get_track_name) = GET_TRACK_NAME {
                                let mut name_buf = vec![0u8; 256];
                                let success = get_track_name(dest_track_ptr, name_buf.as_mut_ptr() as *mut c_char, 256);
                                if success {
                                    let dest_name = std::ffi::CStr::from_ptr(name_buf.as_ptr() as *const c_char)
                                        .to_string_lossy()
                                        .to_string();
                                    send_data.push(OscType::String(dest_name));
                                } else {
                                    send_data.push(OscType::String("Unknown".to_string()));
                                }
                            }
                            
                            // Find destination track index
                            if let Some(count_tracks) = COUNT_TRACKS {
                                if let Some(get_track_fn) = GET_TRACK {
                                    let track_count = count_tracks(std::ptr::null_mut());
                                    let mut dest_index = -1;
                                    for i in 0..track_count {
                                        if get_track_fn(std::ptr::null_mut(), i) == dest_track_ptr {
                                            dest_index = i;
                                            break;
                                        }
                                    }
                                    send_data.push(OscType::Int(dest_index));
                                }
                            }
                        } else {
                            send_data.push(OscType::String("None".to_string()));
                            send_data.push(OscType::Int(-1));
                        }
                        
                        // Send parameters
                        let param = CString::new("D_VOL").unwrap();
                        let volume = get_send_info(track, 0, send_idx, param.as_ptr());
                        send_data.push(OscType::Float(volume as f32));
                        
                        let param = CString::new("D_PAN").unwrap();
                        let pan = get_send_info(track, 0, send_idx, param.as_ptr());
                        send_data.push(OscType::Float(pan as f32));
                        
                        let param = CString::new("B_MUTE").unwrap();
                        let mute = get_send_info(track, 0, send_idx, param.as_ptr());
                        send_data.push(OscType::Bool(mute > 0.0));
                    }
                }
            } else {
                send_data.push(OscType::Int(0)); // No send count available
            }
            
            // Add send data as blob
            response_args.push(OscType::Blob(serialize_osc_array(&send_data)));
            
            // Send response
            let response = OscMessage {
                addr: "/track/scan/response".to_string(),
                args: response_args,
            };
            send_response(response, sender_addr);
            
            show_console_msg(&format!("[renardo-ext] Track scan completed for index {}\n", track_index));
        }
    }
}

/// Helper function to serialize OSC array to bytes
pub fn serialize_osc_array(items: &[OscType]) -> Vec<u8> {
    // Simple serialization - in production, use proper OSC bundle serialization
    let mut bytes = Vec::new();
    
    // Write item count
    bytes.extend_from_slice(&(items.len() as u32).to_be_bytes());
    
    for item in items {
        match item {
            OscType::Int(i) => {
                bytes.push(b'i');
                bytes.extend_from_slice(&i.to_be_bytes());
            }
            OscType::Float(f) => {
                bytes.push(b'f');
                bytes.extend_from_slice(&f.to_be_bytes());
            }
            OscType::String(s) => {
                bytes.push(b's');
                let len = s.len() as u32;
                bytes.extend_from_slice(&len.to_be_bytes());
                bytes.extend_from_slice(s.as_bytes());
            }
            OscType::Bool(b) => {
                bytes.push(b'b');
                bytes.push(if *b { 1 } else { 0 });
            }
            _ => {
                // Unsupported type, write null marker
                bytes.push(b'n');
            }
        }
    }
    
    bytes
}

fn send_error_response(sender_addr: SocketAddr, error_msg: &str) {
    let response = OscMessage {
        addr: "/track/scan/response".to_string(),
        args: vec![
            OscType::String("error".to_string()),
            OscType::String(error_msg.to_string()),
        ],
    };
    send_response(response, sender_addr);
}