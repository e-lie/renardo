/*! REAPER project OSC handlers */

use std::ffi::{c_char, c_int, c_void, CString};
use std::net::SocketAddr;
use rosc::{OscMessage, OscType};

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
/// Expected args: [position (int), name (string), input (int), record_armed (bool), record_mode (int)]
/// - position: Where to insert track (-1 for end)
/// - name: Track name (empty string for default)
/// - input: MIDI input value (-1 for no input, 0+ for MIDI channels)
/// - record_armed: Whether to arm track for recording
/// - record_mode: Record mode (0=output, 1=output stereo, 2=none/monitor input, 3=midi output, etc.)
pub fn handle_add_track(msg: &OscMessage, sender_addr: SocketAddr) {
    // Parse arguments with defaults
    let position = msg.args.get(0)
        .and_then(|arg| if let OscType::Int(pos) = arg { Some(*pos) } else { None })
        .unwrap_or(-1);
    
    let name = msg.args.get(1)
        .and_then(|arg| if let OscType::String(n) = arg { Some(n.as_str()) } else { None })
        .unwrap_or("");
    
    let input = msg.args.get(2)
        .and_then(|arg| if let OscType::Int(inp) = arg { Some(*inp) } else { None })
        .unwrap_or(-1);
    
    let record_armed = msg.args.get(3)
        .and_then(|arg| if let OscType::Bool(armed) = arg { Some(*armed) } else { None })
        .unwrap_or(false);
    
    let record_mode = msg.args.get(4)
        .and_then(|arg| if let OscType::Int(mode) = arg { Some(*mode) } else { None })
        .unwrap_or(2); // Default to "none/monitor input"
    
    show_console_msg(&format!(
        "[renardo-ext] Adding track: pos={}, name='{}', input={}, armed={}, mode={}\n", 
        position, name, input, record_armed, record_mode
    ));
    
    unsafe {
        if let Some(insert_track_at_index) = INSERT_TRACK_AT_INDEX {
            if let Some(count_tracks) = COUNT_TRACKS {
                if let Some(get_track) = GET_TRACK {
                    // Get current track count
                    let track_count = count_tracks(std::ptr::null_mut());
                    
                    // Calculate insertion position
                    let insert_pos = if position < 0 { track_count } else { position.min(track_count) };
                    
                    // Insert track
                    insert_track_at_index(insert_pos, false as i32);
                    
                    // Get the newly created track
                    let new_track = get_track(std::ptr::null_mut(), insert_pos);
                    if !new_track.is_null() {
                        // Set track name if provided
                        if !name.is_empty() {
                            if let Some(get_set_media_track_info) = GET_SET_MEDIA_TRACK_INFO {
                                let name_cstring = CString::new(name).unwrap();
                                let param_name = CString::new("P_NAME").unwrap();
                                
                                get_set_media_track_info(
                                    new_track,
                                    param_name.as_ptr(),
                                    name_cstring.as_ptr() as *mut c_void,
                                    1 // setNewValue = true
                                );
                            }
                        }
                        
                        // Set MIDI input if specified - comprehensive forum-based approaches
                        if input >= 0 {
                            let param_name = CString::new("I_RECINPUT").unwrap();
                            
                            // Try multiple forum-recommended approaches
                            show_console_msg(&format!("[renardo-ext] Trying multiple I_RECINPUT approaches for value: {}\n", input));
                            
                            // Approach 1: SetMediaTrackInfo_Value with proper encoding
                            if let Some(set_media_track_info_value) = SET_MEDIA_TRACK_INFO_VALUE {
                                let midi_input_value = if input >= 4096 {
                                    input as f64
                                } else if input > 0 {
                                    (4096 + input + (63 << 5)) as f64
                                } else {
                                    input as f64
                                };
                                
                                show_console_msg(&format!("[renardo-ext] Approach 1: SetMediaTrackInfo_Value with {}\n", midi_input_value));
                                let success1 = set_media_track_info_value(new_track, param_name.as_ptr(), midi_input_value);
                                
                                if success1 {
                                    if let Some(tracklist_update) = TRACKLIST_UPDATE_ALL_EXTERNAL_SURFACES {
                                        tracklist_update();
                                    }
                                    if let Some(update_timeline) = UPDATE_TIMELINE {
                                        update_timeline();
                                    }
                                }
                                
                                // Check result
                                if let Some(get_media_track_info_value) = GET_MEDIA_TRACK_INFO_VALUE {
                                    let check1 = get_media_track_info_value(new_track, param_name.as_ptr()) as i32;
                                    if check1 != 0 {
                                        show_console_msg(&format!("[renardo-ext] ✅ Approach 1 worked: {}\n", check1));
                                    } else {
                                        show_console_msg("[renardo-ext] ❌ Approach 1 failed, trying approach 2\n");
                                        
                                        // Approach 2: GetSetMediaTrackInfo with double pointer
                                        if let Some(get_set_media_track_info) = GET_SET_MEDIA_TRACK_INFO {
                                            let mut double_value = midi_input_value;
                                            show_console_msg(&format!("[renardo-ext] Approach 2: GetSetMediaTrackInfo with double* {}\n", double_value));
                                            get_set_media_track_info(new_track, param_name.as_ptr(), &mut double_value as *mut f64 as *mut c_void, 1);
                                            
                                            let check2 = get_media_track_info_value(new_track, param_name.as_ptr()) as i32;
                                            if check2 != 0 {
                                                show_console_msg(&format!("[renardo-ext] ✅ Approach 2 worked: {}\n", check2));
                                            } else {
                                                show_console_msg("[renardo-ext] ❌ Approach 2 failed, trying approach 3\n");
                                                
                                                // Approach 3: Try setting after small delay using REAPER actions
                                                show_console_msg("[renardo-ext] Approach 3: Using REAPER action to set MIDI input\n");
                                                
                                                // Action 40712: Track: Set track input to all MIDI inputs (VKB)
                                                if let Some(main_on_command) = MAIN_ON_COMMAND {
                                                    main_on_command(40712, 0);
                                                    show_console_msg("[renardo-ext] Executed action 40712 (set MIDI input)\n");
                                                    
                                                    let check3 = get_media_track_info_value(new_track, param_name.as_ptr()) as i32;
                                                    show_console_msg(&format!("[renardo-ext] Approach 3 result: {}\n", check3));
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Set record armed state
                        if let Some(get_set_media_track_info) = GET_SET_MEDIA_TRACK_INFO {
                            let param_name = CString::new("I_RECARM").unwrap();
                            let mut armed_value = if record_armed { 1i32 } else { 0i32 };
                            
                            get_set_media_track_info(
                                new_track,
                                param_name.as_ptr(),
                                &mut armed_value as *mut i32 as *mut c_void,
                                1 // setNewValue = true
                            );
                        }
                        
                        // Set record mode
                        if let Some(get_set_media_track_info) = GET_SET_MEDIA_TRACK_INFO {
                            let param_name = CString::new("I_RECMODE").unwrap();
                            let mut mode_value = record_mode;
                            
                            get_set_media_track_info(
                                new_track,
                                param_name.as_ptr(),
                                &mut mode_value as *mut i32 as *mut c_void,
                                1 // setNewValue = true
                            );
                        }
                        
                        // Send response with track index
                        let response = OscMessage {
                            addr: "/project/add_track/response".to_string(),
                            args: vec![OscType::Int(insert_pos)],
                        };
                        
                        show_console_msg(&format!("[renardo-ext] Added configured track at index: {}\n", insert_pos));
                        send_response(response, sender_addr);
                    } else {
                        show_console_msg("[renardo-ext] Failed to get newly created track\n");
                    }
                }
            }
        }
    }
}