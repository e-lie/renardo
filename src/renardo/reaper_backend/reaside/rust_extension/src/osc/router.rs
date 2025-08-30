/*! OSC message routing */

use std::net::{UdpSocket, SocketAddr};
use rosc::OscPacket;

use crate::reaper::api::show_console_msg;
use crate::reaper::project::{handle_get_project_name, handle_set_project_name, handle_add_track};
use crate::reaper::track::{handle_get_track_name, handle_set_track_name, handle_get_track_volume, handle_set_track_volume, handle_get_track_pan, handle_set_track_pan, handle_scan_track};
use crate::reaper::fx::{handle_add_fx, handle_remove_fx, handle_get_fx_param, handle_set_fx_param};
use crate::reaper::midi::{handle_play_note};

/// Handle incoming OSC packets
pub fn handle_osc_packet(packet: OscPacket, sender_addr: SocketAddr, _socket: &UdpSocket) {
    match packet {
        OscPacket::Message(msg) => handle_osc_message(msg, sender_addr),
        OscPacket::Bundle(bundle) => {
            for packet in bundle.content {
                handle_osc_packet(packet, sender_addr, _socket);
            }
        }
    }
}

/// Route OSC messages to appropriate handlers
fn handle_osc_message(msg: rosc::OscMessage, sender_addr: SocketAddr) {
    // Log incoming messages (except frequent ones)
    if !msg.addr.starts_with("/project/name/get") {
        show_console_msg(&format!(
            "[renardo-ext] OSC from {}: {}\n", 
            sender_addr, 
            msg.addr
        ));
    }
    
    // Route to appropriate handler based on address
    match msg.addr.as_str() {
        // Project operations
        "/project/name/get" => handle_get_project_name(&msg, sender_addr),
        "/project/name/set" => handle_set_project_name(&msg, sender_addr),
        "/project/add_track" => handle_add_track(&msg, sender_addr),
        
        // Track operations
        "/track/name/get" => handle_get_track_name(&msg, sender_addr),
        "/track/name/set" => handle_set_track_name(&msg, sender_addr),
        "/track/volume/get" => handle_get_track_volume(&msg, sender_addr),
        "/track/volume/set" => handle_set_track_volume(&msg, sender_addr),
        "/track/pan/get" => handle_get_track_pan(&msg, sender_addr),
        "/track/pan/set" => handle_set_track_pan(&msg, sender_addr),
        "/track/scan" => handle_scan_track(&msg, sender_addr),
        
        // FX operations (placeholders)
        "/fx/add" => handle_add_fx(&msg, sender_addr),
        "/fx/remove" => handle_remove_fx(&msg, sender_addr),
        "/fx/param/get" => handle_get_fx_param(&msg, sender_addr),
        "/fx/param/set" => handle_set_fx_param(&msg, sender_addr),
        
        // MIDI operations
        "/note" => handle_play_note(&msg, sender_addr),
        
        // Unknown routes
        _ => {
            show_console_msg(&format!(
                "[renardo-ext] Unknown route: {}\n", 
                msg.addr
            ));
        }
    }
}