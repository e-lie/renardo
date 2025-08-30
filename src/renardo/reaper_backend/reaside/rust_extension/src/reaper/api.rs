/*! REAPER API function pointers and core bindings */

use std::ffi::{c_char, c_int, c_void, CString};

// REAPER API function pointers - global statics for C FFI
pub static mut SHOW_CONSOLE_MSG: Option<extern "C" fn(*const c_char)> = None;
pub static mut GET_PROJECT_NAME: Option<extern "C" fn(*mut c_void, *mut c_char, c_int)> = None;
pub static mut ENUM_PROJECTS: Option<extern "C" fn(c_int) -> *mut c_void> = None;
pub static mut GET_SET_MEDIA_TRACK_INFO: Option<extern "C" fn(*mut c_void, *const c_char, *mut c_void, c_int)> = None;
pub static mut MAIN_ON_COMMAND: Option<extern "C" fn(c_int, c_int)> = None;
pub static mut INSERT_TRACK_AT_INDEX: Option<extern "C" fn(c_int, c_int)> = None;
pub static mut COUNT_TRACKS: Option<extern "C" fn(*mut c_void) -> c_int> = None;
pub static mut GET_TRACK: Option<extern "C" fn(*mut c_void, c_int) -> *mut c_void> = None;
pub static mut GET_TRACK_NAME: Option<extern "C" fn(*mut c_void, *mut c_char, c_int) -> bool> = None;
pub static mut STUFF_MIDI_MESSAGE: Option<extern "C" fn(c_int, c_int, c_int, c_int)> = None;

// FX API functions
pub static mut TRACK_FX_GET_COUNT: Option<extern "C" fn(*mut c_void) -> c_int> = None;
pub static mut TRACK_FX_GET_FX_NAME: Option<extern "C" fn(*mut c_void, c_int, *mut c_char, c_int) -> bool> = None;
pub static mut TRACK_FX_GET_ENABLED: Option<extern "C" fn(*mut c_void, c_int) -> bool> = None;
pub static mut TRACK_FX_GET_PRESET: Option<extern "C" fn(*mut c_void, c_int, *mut c_char, c_int) -> bool> = None;
pub static mut TRACK_FX_GET_NUM_PARAMS: Option<extern "C" fn(*mut c_void, c_int) -> c_int> = None;
pub static mut TRACK_FX_GET_PARAM_NAME: Option<extern "C" fn(*mut c_void, c_int, c_int, *mut c_char, c_int) -> bool> = None;
pub static mut TRACK_FX_GET_PARAM: Option<extern "C" fn(*mut c_void, c_int, c_int, *mut f64, *mut f64) -> f64> = None;
pub static mut TRACK_FX_GET_FORMATTED_PARAM_VALUE: Option<extern "C" fn(*mut c_void, c_int, c_int, *mut c_char, c_int) -> bool> = None;

// Send API functions  
pub static mut GET_TRACK_NUM_SENDS: Option<extern "C" fn(*mut c_void, c_int) -> c_int> = None;
pub static mut GET_TRACK_SEND_INFO_VALUE: Option<extern "C" fn(*mut c_void, c_int, c_int, *const c_char) -> f64> = None;
pub static mut GET_TRACK_SEND_NAME: Option<extern "C" fn(*mut c_void, c_int, *mut c_char, c_int) -> bool> = None;

// Track color
pub static mut GET_TRACK_COLOR: Option<extern "C" fn(*mut c_void) -> c_int> = None;

/// REAPER plugin info struct for interfacing with REAPER
#[repr(C)]
pub struct ReaperPluginInfo {
    pub caller_version: c_int,
    pub hwnd_main: *mut c_void,
    pub register: Option<extern "C" fn(*const c_char, *mut c_void) -> c_int>,
    pub get_func: Option<extern "C" fn(*const c_char) -> *mut c_void>,
}

/// Initialize REAPER API function pointers
pub fn initialize_api(plugin_info: &ReaperPluginInfo) {
    unsafe {
        if let Some(get_func) = plugin_info.get_func {
            // Core functions
            init_function_pointer(&get_func, "ShowConsoleMsg", &mut SHOW_CONSOLE_MSG);
            init_function_pointer(&get_func, "GetProjectName", &mut GET_PROJECT_NAME);
            init_function_pointer(&get_func, "EnumProjects", &mut ENUM_PROJECTS);
            init_function_pointer(&get_func, "Main_OnCommand", &mut MAIN_ON_COMMAND);
            init_function_pointer(&get_func, "GetSetMediaTrackInfo", &mut GET_SET_MEDIA_TRACK_INFO);
            init_function_pointer(&get_func, "InsertTrackAtIndex", &mut INSERT_TRACK_AT_INDEX);
            init_function_pointer(&get_func, "CountTracks", &mut COUNT_TRACKS);
            init_function_pointer(&get_func, "GetTrack", &mut GET_TRACK);
            init_function_pointer(&get_func, "GetTrackName", &mut GET_TRACK_NAME);
            init_function_pointer(&get_func, "StuffMIDIMessage", &mut STUFF_MIDI_MESSAGE);
            
            // FX functions
            init_function_pointer(&get_func, "TrackFX_GetCount", &mut TRACK_FX_GET_COUNT);
            init_function_pointer(&get_func, "TrackFX_GetFXName", &mut TRACK_FX_GET_FX_NAME);
            init_function_pointer(&get_func, "TrackFX_GetEnabled", &mut TRACK_FX_GET_ENABLED);
            init_function_pointer(&get_func, "TrackFX_GetPreset", &mut TRACK_FX_GET_PRESET);
            init_function_pointer(&get_func, "TrackFX_GetNumParams", &mut TRACK_FX_GET_NUM_PARAMS);
            init_function_pointer(&get_func, "TrackFX_GetParamName", &mut TRACK_FX_GET_PARAM_NAME);
            init_function_pointer(&get_func, "TrackFX_GetParam", &mut TRACK_FX_GET_PARAM);
            init_function_pointer(&get_func, "TrackFX_GetFormattedParamValue", &mut TRACK_FX_GET_FORMATTED_PARAM_VALUE);
            
            // Send functions
            init_function_pointer(&get_func, "GetTrackNumSends", &mut GET_TRACK_NUM_SENDS);
            init_function_pointer(&get_func, "GetTrackSendInfo_Value", &mut GET_TRACK_SEND_INFO_VALUE);
            init_function_pointer(&get_func, "GetTrackSendName", &mut GET_TRACK_SEND_NAME);
            
            // Track color
            init_function_pointer(&get_func, "GetTrackColor", &mut GET_TRACK_COLOR);
        }
    }
}

/// Helper function to initialize a single function pointer
unsafe fn init_function_pointer<T>(
    get_func: &extern "C" fn(*const c_char) -> *mut c_void,
    name: &str,
    target: &mut Option<T>
) {
    let func_name = CString::new(name).unwrap();
    let func_ptr = get_func(func_name.as_ptr());
    if !func_ptr.is_null() {
        *target = Some(std::mem::transmute_copy(&func_ptr));
    }
}

/// Safe wrapper to show messages in REAPER console
pub fn show_console_msg(message: &str) {
    unsafe {
        if let Some(show_msg) = SHOW_CONSOLE_MSG {
            if let Ok(c_message) = CString::new(message) {
                show_msg(c_message.as_ptr());
            }
        }
    }
}