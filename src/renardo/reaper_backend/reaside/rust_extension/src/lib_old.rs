use std::error::Error;
use std::ffi::{CString, c_void};
use std::net::UdpSocket;
use std::os::raw::{c_char, c_int};
use std::ptr;
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use once_cell::sync::Lazy;
use parking_lot::Mutex;
use rosc::{OscPacket, OscMessage, OscType, encoder};

// REAPER API function pointers
static mut SHOW_CONSOLE_MSG: Option<extern "C" fn(*const c_char)> = None;
static mut GET_PROJECT_NAME: Option<extern "C" fn(*mut c_void, *mut c_char, c_int)> = None;
static mut ENUM_PROJECTS: Option<extern "C" fn(c_int) -> *mut c_void> = None;
static mut GET_SET_MEDIA_TRACK_INFO: Option<extern "C" fn(*mut c_void, *const c_char, *mut c_void, c_int)> = None;
static mut MAIN_ON_COMMAND: Option<extern "C" fn(c_int, c_int)> = None;
static mut INSERT_TRACK_AT_INDEX: Option<extern "C" fn(c_int, c_int)> = None;
static mut COUNT_TRACKS: Option<extern "C" fn(*mut c_void) -> c_int> = None;
static mut GET_TRACK: Option<extern "C" fn(*mut c_void, c_int) -> *mut c_void> = None;
static mut GET_TRACK_NAME: Option<extern "C" fn(*mut c_void, *mut c_char, c_int) -> bool> = None;

// Global state for the OSC server
static OSC_SERVER: Lazy<Arc<Mutex<Option<OscServer>>>> = Lazy::new(|| Arc::new(Mutex::new(None)));

// REAPER plugin info struct
#[repr(C)]
struct ReaperPluginInfo {
    caller_version: c_int,
    hwnd_main: *mut c_void,
    register: Option<extern "C" fn(*const c_char, *mut c_void) -> c_int>,
    get_func: Option<extern "C" fn(*const c_char) -> *mut c_void>,
}

struct OscServer {
    socket: UdpSocket,
    client_socket: UdpSocket,
    running: Arc<Mutex<bool>>,
}

impl OscServer {
    fn new(server_port: u16, client_port: u16) -> Result<Self, Box<dyn Error>> {
        let socket = UdpSocket::bind(format!("127.0.0.1:{}", server_port))?;
        socket.set_nonblocking(true)?;
        
        let client_socket = UdpSocket::bind("127.0.0.1:0")?;  // Bind to any available port
        client_socket.connect(format!("127.0.0.1:{}", client_port))?;
        
        Ok(OscServer {
            socket,
            client_socket,
            running: Arc::new(Mutex::new(true)),
        })
    }
    
    fn send_response(&self, msg: OscMessage) -> Result<(), Box<dyn Error>> {
        let packet = OscPacket::Message(msg);
        let buf = encoder::encode(&packet)?;
        self.client_socket.send(&buf)?;
        Ok(())
    }
    
    fn start(&self) {
        let socket = self.socket.try_clone().expect("Failed to clone socket");
        let client_socket = self.client_socket.try_clone().expect("Failed to clone client socket");
        let running = self.running.clone();
        
        thread::spawn(move || {
            let mut buf = [0u8; 1024];
            
            while *running.lock() {
                match socket.recv_from(&mut buf) {
                    Ok((size, addr)) => {
                        match rosc::decoder::decode_udp(&buf[..size]) {
                            Ok((_remaining, packet)) => {
                                handle_osc_packet(packet, addr, &client_socket);
                            }
                            Err(e) => {
                                show_console_msg(&format!("OSC decode error: {:?}\n", e));
                            }
                        }
                    }
                    Err(ref e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                        // No data available, sleep briefly
                        thread::sleep(Duration::from_millis(10));
                    }
                    Err(e) => {
                        show_console_msg(&format!("OSC receive error: {}\n", e));
                    }
                }
            }
        });
    }
    
    fn stop(&self) {
        *self.running.lock() = false;
    }
}

fn handle_osc_packet(packet: OscPacket, sender_addr: std::net::SocketAddr, _client_socket: &UdpSocket) {
    match packet {
        OscPacket::Message(msg) => handle_osc_message(msg, sender_addr),
        OscPacket::Bundle(bundle) => {
            for packet in bundle.content {
                handle_osc_packet(packet, sender_addr, _client_socket);
            }
        }
    }
}

fn handle_osc_message(msg: OscMessage, sender_addr: std::net::SocketAddr) {
    // Log incoming messages (except frequent ones)
    if !msg.addr.starts_with("/project/name/get") {
        show_console_msg(&format!(
            "[renardo-ext] OSC from {}: {}\n", 
            sender_addr, 
            msg.addr
        ));
    }
    
    // Handle specific routes
    match msg.addr.as_str() {
        "/project/name/get" => {
            // Get current project name
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
                            
                            let packet = OscPacket::Message(response);
                            if let Ok(buf) = encoder::encode(&packet) {
                                // Send response to fixed client port 9878
                                let response_socket = UdpSocket::bind("127.0.0.1:0").expect("Failed to create response socket");
                                let client_addr = std::net::SocketAddr::new(sender_addr.ip(), 9878);
                                match response_socket.send_to(&buf, client_addr) {
                                    Ok(_) => show_console_msg(&format!("[renardo-ext] Sent project name response to {}\n", client_addr)),
                                    Err(e) => show_console_msg(&format!("[renardo-ext] Failed to send response to {}: {}\n", client_addr, e)),
                                }
                            } else {
                                show_console_msg("[renardo-ext] Failed to encode OSC response\n");
                            }
                        }
                    }
                }
            }
        }
        "/project/name/set" => {
            // Set project name
            if let Some(OscType::String(new_name)) = msg.args.get(0) {
                show_console_msg(&format!("[renardo-ext] Setting project name to: {}\n", new_name));
                
                // Use Main_OnCommand to trigger "Save project as..." with the new name
                // Command 40022 = File: Save project as...
                unsafe {
                    if let Some(main_on_command) = MAIN_ON_COMMAND {
                        // This will open the save dialog - we can't directly set the name
                        // For now, just log that we received the request
                        show_console_msg(&format!("[renardo-ext] Note: Direct project rename not available via API, would need save dialog\n"));
                        
                        // Send response indicating limitation
                        let response = OscMessage {
                            addr: "/project/name/response".to_string(),
                            args: vec![
                                OscType::String("limited".to_string()),
                                OscType::String(new_name.clone()),
                            ],
                        };
                        
                        let packet = OscPacket::Message(response);
                        if let Ok(buf) = encoder::encode(&packet) {
                            // Send response to fixed client port 9878
                            let response_socket = UdpSocket::bind("127.0.0.1:0").expect("Failed to create response socket");
                            let client_addr = std::net::SocketAddr::new(sender_addr.ip(), 9878);
                            match response_socket.send_to(&buf, client_addr) {
                                Ok(_) => show_console_msg(&format!("[renardo-ext] Sent set response to {}\n", client_addr)),
                                Err(e) => show_console_msg(&format!("[renardo-ext] Failed to send set response to {}: {}\n", client_addr, e)),
                            }
                        }
                    }
                }
            }
        }
        "/project/add_track" => {
            // Add a new track to the project
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
                        
                        let packet = OscPacket::Message(response);
                        if let Ok(buf) = encoder::encode(&packet) {
                            // Send response to fixed client port 9878
                            let response_socket = UdpSocket::bind("127.0.0.1:0").expect("Failed to create response socket");
                            let client_addr = std::net::SocketAddr::new(sender_addr.ip(), 9878);
                            match response_socket.send_to(&buf, client_addr) {
                                Ok(_) => show_console_msg(&format!("[renardo-ext] Sent add_track response: {} to {}\n", track_count, client_addr)),
                                Err(e) => show_console_msg(&format!("[renardo-ext] Failed to send add_track response: {}\n", e)),
                            }
                        }
                    }
                }
            }
        }
        "/track/name/get" => {
            // Get track name - expecting track index as first argument
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
                                    
                                    let packet = OscPacket::Message(response);
                                    if let Ok(buf) = encoder::encode(&packet) {
                                        let response_socket = UdpSocket::bind("127.0.0.1:0").expect("Failed to create response socket");
                                        let client_addr = std::net::SocketAddr::new(sender_addr.ip(), 9878);
                                        match response_socket.send_to(&buf, client_addr) {
                                            Ok(_) => show_console_msg(&format!("[renardo-ext] Sent track name response to {}\n", client_addr)),
                                            Err(e) => show_console_msg(&format!("[renardo-ext] Failed to send track name response: {}\n", e)),
                                        }
                                    }
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
        "/track/name/set" => {
            // Set track name - expecting track index and name as arguments
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
                                let name_cstring = std::ffi::CString::new(new_name.as_str()).unwrap();
                                let param_name = std::ffi::CString::new("P_NAME").unwrap();
                                
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
                                
                                let packet = OscPacket::Message(response);
                                if let Ok(buf) = encoder::encode(&packet) {
                                    let response_socket = UdpSocket::bind("127.0.0.1:0").expect("Failed to create response socket");
                                    let client_addr = std::net::SocketAddr::new(sender_addr.ip(), 9878);
                                    match response_socket.send_to(&buf, client_addr) {
                                        Ok(_) => show_console_msg(&format!("[renardo-ext] Sent track set name response to {}\n", client_addr)),
                                        Err(e) => show_console_msg(&format!("[renardo-ext] Failed to send track set name response: {}\n", e)),
                                    }
                                }
                            } else {
                                show_console_msg(&format!("[renardo-ext] Track {} not found for name setting\n", track_index));
                            }
                        }
                    }
                }
            }
        }
        _ => {
            show_console_msg(&format!(
                "[renardo-ext] Unknown route: {}\n", 
                msg.addr
            ));
        }
    }
}

// Helper function to show messages in REAPER console
fn show_console_msg(msg: &str) {
    unsafe {
        if let Some(func) = SHOW_CONSOLE_MSG {
            if let Ok(c_str) = CString::new(msg) {
                func(c_str.as_ptr());
            }
        }
    }
}

// REAPER extension entry point
#[no_mangle]
pub extern "C" fn ReaperPluginEntry(
    _hinstance: *mut c_void,
    rec: *mut ReaperPluginInfo,
) -> c_int {
    if rec.is_null() {
        // Cleanup on unload
        if let Some(server) = OSC_SERVER.lock().take() {
            server.stop();
            show_console_msg("[renardo-ext] OSC server stopped\n");
        }
        return 0;
    }
    
    unsafe {
        // Get REAPER API functions
        let plugin_info = &*rec;
        
        if let Some(get_func) = plugin_info.get_func {
            // Get ShowConsoleMsg function
            let func_name = CString::new("ShowConsoleMsg").unwrap();
            let func_ptr = get_func(func_name.as_ptr());
            if !func_ptr.is_null() {
                SHOW_CONSOLE_MSG = Some(std::mem::transmute(func_ptr));
            }
            
            // Get GetProjectName function
            let func_name = CString::new("GetProjectName").unwrap();
            let func_ptr = get_func(func_name.as_ptr());
            if !func_ptr.is_null() {
                GET_PROJECT_NAME = Some(std::mem::transmute(func_ptr));
            }
            
            // Get EnumProjects function
            let func_name = CString::new("EnumProjects").unwrap();
            let func_ptr = get_func(func_name.as_ptr());
            if !func_ptr.is_null() {
                ENUM_PROJECTS = Some(std::mem::transmute(func_ptr));
            }
            
            // Get Main_OnCommand function
            let func_name = CString::new("Main_OnCommand").unwrap();
            let func_ptr = get_func(func_name.as_ptr());
            if !func_ptr.is_null() {
                MAIN_ON_COMMAND = Some(std::mem::transmute(func_ptr));
            }
            
            // Get GetSetMediaTrackInfo function
            let func_name = CString::new("GetSetMediaTrackInfo").unwrap();
            let func_ptr = get_func(func_name.as_ptr());
            if !func_ptr.is_null() {
                GET_SET_MEDIA_TRACK_INFO = Some(std::mem::transmute(func_ptr));
            }
            
            // Get InsertTrackAtIndex function
            let func_name = CString::new("InsertTrackAtIndex").unwrap();
            let func_ptr = get_func(func_name.as_ptr());
            if !func_ptr.is_null() {
                INSERT_TRACK_AT_INDEX = Some(std::mem::transmute(func_ptr));
            }
            
            // Get CountTracks function
            let func_name = CString::new("CountTracks").unwrap();
            let func_ptr = get_func(func_name.as_ptr());
            if !func_ptr.is_null() {
                COUNT_TRACKS = Some(std::mem::transmute(func_ptr));
            }
            
            // Get GetTrack function
            let func_name = CString::new("GetTrack").unwrap();
            let func_ptr = get_func(func_name.as_ptr());
            if !func_ptr.is_null() {
                GET_TRACK = Some(std::mem::transmute(func_ptr));
            }
            
            // Get GetTrackName function
            let func_name = CString::new("GetTrackName").unwrap();
            let func_ptr = get_func(func_name.as_ptr());
            if !func_ptr.is_null() {
                GET_TRACK_NAME = Some(std::mem::transmute(func_ptr));
            }
        }
    }
    
    // Initialize extension
    show_console_msg("=================================\n");
    show_console_msg("Renardo REAPER Extension loaded!\n");
    show_console_msg("=================================\n");
    
    // Start OSC server on ports 9877 (receive) and 9878 (send)
    let server_port = 9877;
    let client_port = 9878;
    match OscServer::new(server_port, client_port) {
        Ok(server) => {
            show_console_msg(&format!("[renardo-ext] OSC server listening on port {}\n", server_port));
            show_console_msg(&format!("[renardo-ext] OSC client sending to port {}\n", client_port));
            show_console_msg("[renardo-ext] Available routes:\n");
            show_console_msg("[renardo-ext]   /project/name/get - Get current project name\n");
            show_console_msg("[renardo-ext]   /project/name/set - Set project name (limited)\n");
            
            server.start();
            
            // Store the server globally
            *OSC_SERVER.lock() = Some(server);
        }
        Err(e) => {
            show_console_msg(&format!("[renardo-ext] Failed to start OSC server: {}\n", e));
        }
    }
    
    1  // Return 1 to indicate success
}