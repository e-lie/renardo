/*! OSC server implementation */

use std::net::UdpSocket;
use std::sync::Arc;
use std::thread;
use std::time::Duration;
use std::error::Error;

use rosc::{OscPacket, decoder};

use crate::reaper::api::show_console_msg;
use crate::osc::router::handle_osc_packet;

/// OSC Server for handling bidirectional OSC communication
pub struct OscServer {
    socket: Arc<UdpSocket>,
    client_port: u16,
}

impl OscServer {
    /// Create a new OSC server
    pub fn new(server_port: u16, client_port: u16) -> Result<Self, Box<dyn Error>> {
        let socket = UdpSocket::bind(format!("127.0.0.1:{}", server_port))?;
        socket.set_read_timeout(Some(Duration::from_millis(100)))?;
        
        let server = OscServer {
            socket: Arc::new(socket),
            client_port,
        };
        
        // Start listening thread
        server.start_listening();
        
        Ok(server)
    }
    
    /// Start the listening thread
    fn start_listening(&self) {
        let socket = self.socket.clone();
        
        thread::spawn(move || {
            let mut buf = [0u8; rosc::decoder::MTU];
            
            loop {
                match socket.recv_from(&mut buf) {
                    Ok((size, sender_addr)) => {
                        if let Ok(packet) = decoder::decode_udp(&buf[..size]) {
                            handle_osc_packet(packet.1, sender_addr, &socket);
                        }
                    }
                    Err(_) => {
                        // Timeout or other error - continue listening
                        thread::sleep(Duration::from_millis(10));
                    }
                }
            }
        });
    }
}

/// Global OSC server storage
use once_cell::sync::Lazy;
use parking_lot::Mutex;

pub static OSC_SERVER: Lazy<Arc<Mutex<Option<OscServer>>>> = 
    Lazy::new(|| Arc::new(Mutex::new(None)));