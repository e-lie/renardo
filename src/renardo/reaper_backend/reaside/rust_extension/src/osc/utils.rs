/*! OSC utilities */

use std::net::{UdpSocket, SocketAddr};
use rosc::{OscMessage, OscPacket, encoder};

use crate::reaper::api::show_console_msg;

/// Send an OSC response message to the client
pub fn send_response(response: OscMessage, sender_addr: SocketAddr) {
    let packet = OscPacket::Message(response);
    if let Ok(buf) = encoder::encode(&packet) {
        // Send response to fixed client port 9878
        let response_socket = UdpSocket::bind("127.0.0.1:0").expect("Failed to create response socket");
        let client_addr = SocketAddr::new(sender_addr.ip(), 9878);
        match response_socket.send_to(&buf, client_addr) {
            Ok(_) => {
                // Only log successful sends for debugging if needed
                // show_console_msg(&format!("[renardo-ext] Sent response to {}\n", client_addr));
            }
            Err(e) => {
                show_console_msg(&format!("[renardo-ext] Failed to send response: {}\n", e));
            }
        }
    } else {
        show_console_msg("[renardo-ext] Failed to encode OSC response\n");
    }
}