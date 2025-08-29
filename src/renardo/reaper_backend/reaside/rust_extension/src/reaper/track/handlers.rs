/*! REAPER track OSC handlers */

use std::ffi::{c_char, c_void, CString};
use std::net::SocketAddr;
use rosc::{OscMessage, OscType};

use crate::reaper::api::*;
use crate::osc::send_response;

/// Handle OSC route: /track/name/get
pub fn handle_get_track_name(msg: &OscMessage, sender_addr: SocketAddr) {
    if let Some(OscType::Int(track_index)) = msg.args.get(0) {
        show_console_msg(&format!("[renardo-ext] Getting name for track {}\n", track_index));
        
        unsafe {
            if let Some(get_track) = GET_TRACK {
                if let Some(get_track_name) = GET_TRACK_NAME {
                    // Get the track
                    let track = get_track(std::ptr::null_mut(), *track_index);
                    if !track.is_null() {
                        let mut buf = vec![0u8; 256];
                        let success = get_track_name(track, buf.as_mut_ptr() as *mut c_char, 256);
                        
                        if success {
                            // Convert to string safely
                            let track_name = std::ffi::CStr::from_ptr(buf.as_ptr() as *const c_char)
                                .to_string_lossy()
                                .to_string();
                            
                            show_console_msg(&format!("[renardo-ext] Got track {} name: '{}'\n", track_index, track_name));
                            
                            // Send response
                            let response = OscMessage {
                                addr: "/track/name/get/response".to_string(),
                                args: vec![
                                    OscType::Int(*track_index),
                                    OscType::String(track_name)
                                ],
                            };
                            
                            send_response(response, sender_addr);
                        } else {
                            show_console_msg(&format!("[renardo-ext] Failed to get track {} name\n", track_index));
                        }
                    } else {
                        show_console_msg(&format!("[renardo-ext] Track {} not found\n", track_index));
                    }
                }
            }
        }
    }
}

/// Handle OSC route: /track/name/set
pub fn handle_set_track_name(msg: &OscMessage, sender_addr: SocketAddr) {
    if let (Some(OscType::Int(track_index)), Some(OscType::String(new_name))) = 
        (msg.args.get(0), msg.args.get(1)) {
        
        show_console_msg(&format!("[renardo-ext] Setting track {} name to: '{}'\n", track_index, new_name));
        
        unsafe {
            if let Some(get_track) = GET_TRACK {
                if let Some(get_set_media_track_info) = GET_SET_MEDIA_TRACK_INFO {
                    // Get the track
                    let track = get_track(std::ptr::null_mut(), *track_index);
                    if !track.is_null() {
                        // Set track name using GetSetMediaTrackInfo
                        let name_cstring = CString::new(new_name.as_str()).unwrap();
                        let param_name = CString::new("P_NAME").unwrap();
                        
                        get_set_media_track_info(
                            track,
                            param_name.as_ptr(),
                            name_cstring.as_ptr() as *mut c_void,
                            1 // setNewValue = true
                        );
                        
                        // Send success response
                        let response = OscMessage {
                            addr: "/track/name/set/response".to_string(),
                            args: vec![
                                OscType::Int(*track_index),
                                OscType::String(new_name.clone()),
                                OscType::String("success".to_string())
                            ],
                        };
                        
                        send_response(response, sender_addr);
                    } else {
                        show_console_msg(&format!("[renardo-ext] Track {} not found for name setting\n", track_index));
                    }
                }
            }
        }
    }
}

/// Handle OSC route: /track/volume/get
pub fn handle_get_track_volume(msg: &OscMessage, sender_addr: SocketAddr) {
    if let Some(OscType::Int(track_index)) = msg.args.get(0) {
        show_console_msg(&format!("[renardo-ext] Getting volume for track {}\n", track_index));
        
        unsafe {
            if let Some(get_track) = GET_TRACK {
                if let Some(get_set_media_track_info) = GET_SET_MEDIA_TRACK_INFO {
                    let track = get_track(std::ptr::null_mut(), *track_index);
                    if !track.is_null() {
                        let param_name = CString::new("D_VOL").unwrap();
                        let mut volume_value: f64 = 0.0;
                        
                        get_set_media_track_info(
                            track,
                            param_name.as_ptr(),
                            &mut volume_value as *mut f64 as *mut c_void,
                            0 // setNewValue = false (get)
                        );
                        
                        let response = OscMessage {
                            addr: "/track/volume/get/response".to_string(),
                            args: vec![
                                OscType::Int(*track_index),
                                OscType::Float(volume_value as f32)
                            ],
                        };
                        
                        send_response(response, sender_addr);
                    }
                }
            }
        }
    }
}

/// Handle OSC route: /track/volume/set
pub fn handle_set_track_volume(msg: &OscMessage, sender_addr: SocketAddr) {
    if let (Some(OscType::Int(track_index)), Some(volume_arg)) = 
        (msg.args.get(0), msg.args.get(1)) {
        
        let volume = match volume_arg {
            OscType::Float(v) => *v as f64,
            OscType::Double(v) => *v,
            OscType::Int(v) => *v as f64,
            _ => return,
        };
        
        show_console_msg(&format!("[renardo-ext] Setting track {} volume to: {}\n", track_index, volume));
        
        unsafe {
            if let Some(get_track) = GET_TRACK {
                if let Some(get_set_media_track_info) = GET_SET_MEDIA_TRACK_INFO {
                    let track = get_track(std::ptr::null_mut(), *track_index);
                    if !track.is_null() {
                        let param_name = CString::new("D_VOL").unwrap();
                        let mut volume_value = volume;
                        
                        get_set_media_track_info(
                            track,
                            param_name.as_ptr(),
                            &mut volume_value as *mut f64 as *mut c_void,
                            1 // setNewValue = true
                        );
                        
                        let response = OscMessage {
                            addr: "/track/volume/set/response".to_string(),
                            args: vec![
                                OscType::Int(*track_index),
                                OscType::Float(volume as f32),
                                OscType::String("success".to_string())
                            ],
                        };
                        
                        send_response(response, sender_addr);
                    }
                }
            }
        }
    }
}

/// Handle OSC route: /track/pan/get
pub fn handle_get_track_pan(msg: &OscMessage, sender_addr: SocketAddr) {
    if let Some(OscType::Int(track_index)) = msg.args.get(0) {
        show_console_msg(&format!("[renardo-ext] Getting pan for track {}\n", track_index));
        
        unsafe {
            if let Some(get_track) = GET_TRACK {
                if let Some(get_set_media_track_info) = GET_SET_MEDIA_TRACK_INFO {
                    let track = get_track(std::ptr::null_mut(), *track_index);
                    if !track.is_null() {
                        let param_name = CString::new("D_PAN").unwrap();
                        let mut pan_value: f64 = 0.0;
                        
                        get_set_media_track_info(
                            track,
                            param_name.as_ptr(),
                            &mut pan_value as *mut f64 as *mut c_void,
                            0 // setNewValue = false (get)
                        );
                        
                        let response = OscMessage {
                            addr: "/track/pan/get/response".to_string(),
                            args: vec![
                                OscType::Int(*track_index),
                                OscType::Float(pan_value as f32)
                            ],
                        };
                        
                        send_response(response, sender_addr);
                    }
                }
            }
        }
    }
}

/// Handle OSC route: /track/pan/set
pub fn handle_set_track_pan(msg: &OscMessage, sender_addr: SocketAddr) {
    if let (Some(OscType::Int(track_index)), Some(pan_arg)) = 
        (msg.args.get(0), msg.args.get(1)) {
        
        let pan = match pan_arg {
            OscType::Float(v) => *v as f64,
            OscType::Double(v) => *v,
            OscType::Int(v) => *v as f64,
            _ => return,
        };
        
        show_console_msg(&format!("[renardo-ext] Setting track {} pan to: {}\n", track_index, pan));
        
        unsafe {
            if let Some(get_track) = GET_TRACK {
                if let Some(get_set_media_track_info) = GET_SET_MEDIA_TRACK_INFO {
                    let track = get_track(std::ptr::null_mut(), *track_index);
                    if !track.is_null() {
                        let param_name = CString::new("D_PAN").unwrap();
                        let mut pan_value = pan;
                        
                        get_set_media_track_info(
                            track,
                            param_name.as_ptr(),
                            &mut pan_value as *mut f64 as *mut c_void,
                            1 // setNewValue = true
                        );
                        
                        let response = OscMessage {
                            addr: "/track/pan/set/response".to_string(),
                            args: vec![
                                OscType::Int(*track_index),
                                OscType::Float(pan as f32),
                                OscType::String("success".to_string())
                            ],
                        };
                        
                        send_response(response, sender_addr);
                    }
                }
            }
        }
    }
}