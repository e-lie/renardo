use std::error::Error;
use std::ffi::{CString, c_void};
use std::net::UdpSocket;
use std::os::raw::{c_char, c_int};
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use once_cell::sync::Lazy;
use parking_lot::Mutex;
use rosc::{OscPacket, OscMessage, OscType};

// REAPER API function pointers
static mut SHOW_CONSOLE_MSG: Option<extern "C" fn(*const c_char)> = None;

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
    running: Arc<Mutex<bool>>,
}

impl OscServer {
    fn new(port: u16) -> Result<Self, Box<dyn Error>> {
        let socket = UdpSocket::bind(format!("127.0.0.1:{}", port))?;
        socket.set_nonblocking(true)?;
        
        Ok(OscServer {
            socket,
            running: Arc::new(Mutex::new(true)),
        })
    }
    
    fn start(&self) {
        let socket = self.socket.try_clone().expect("Failed to clone socket");
        let running = self.running.clone();
        
        thread::spawn(move || {
            let mut buf = [0u8; 1024];
            
            while *running.lock() {
                match socket.recv_from(&mut buf) {
                    Ok((size, addr)) => {
                        match rosc::decoder::decode_udp(&buf[..size]) {
                            Ok((_remaining, packet)) => {
                                handle_osc_packet(packet, addr);
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

fn handle_osc_packet(packet: OscPacket, addr: std::net::SocketAddr) {
    match packet {
        OscPacket::Message(msg) => handle_osc_message(msg, addr),
        OscPacket::Bundle(bundle) => {
            for packet in bundle.content {
                handle_osc_packet(packet, addr);
            }
        }
    }
}

fn handle_osc_message(msg: OscMessage, addr: std::net::SocketAddr) {
    // Log all incoming messages
    show_console_msg(&format!(
        "[renardo-ext] OSC from {}: {}\n", 
        addr, 
        msg.addr
    ));
    
    // Handle specific routes
    match msg.addr.as_str() {
        "/demo/args" => {
            show_console_msg("[renardo-ext] /demo/args route triggered\n");
            
            // Log all arguments
            for (i, arg) in msg.args.iter().enumerate() {
                let arg_str = match arg {
                    OscType::Int(v) => format!("Int({})", v),
                    OscType::Float(v) => format!("Float({})", v),
                    OscType::String(v) => format!("String(\"{}\")", v),
                    OscType::Double(v) => format!("Double({})", v),
                    OscType::Long(v) => format!("Long({})", v),
                    OscType::Bool(v) => format!("Bool({})", v),
                    OscType::Char(v) => format!("Char('{}')", v),
                    _ => format!("{:?}", arg),
                };
                
                show_console_msg(&format!(
                    "[renardo-ext]   arg[{}]: {}\n", 
                    i, 
                    arg_str
                ));
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
        }
    }
    
    // Initialize extension
    show_console_msg("=================================\n");
    show_console_msg("Renardo REAPER Extension loaded!\n");
    show_console_msg("=================================\n");
    
    // Start OSC server on port 9000
    let port = 9000;
    match OscServer::new(port) {
        Ok(server) => {
            show_console_msg(&format!("[renardo-ext] OSC server started on port {}\n", port));
            show_console_msg("[renardo-ext] Listening for OSC messages...\n");
            show_console_msg("[renardo-ext] Test with: /demo/args\n");
            
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