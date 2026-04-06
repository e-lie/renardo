/*! OSC message routing */

use std::net::{UdpSocket, SocketAddr};
use rosc::OscPacket;

use crate::reaper::api::show_console_msg;
use crate::reaper::project::{handle_track_count, handle_get_tempo, handle_set_tempo};
use crate::reaper::track::{handle_get_track_name, handle_set_track_name, handle_get_track_volume, handle_set_track_volume, handle_get_track_pan, handle_set_track_pan, handle_scan_track};
use crate::reaper::fx::{handle_add_fx, handle_remove_fx, handle_get_fx_param, handle_set_fx_param, handle_scan_fx_params};
use crate::reaper::midi::handle_play_note;

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
    show_console_msg(&format!(
        "[renardo-fresh] OSC: {}\n",
        msg.addr
    ));

    match msg.addr.as_str() {
        // Project operations
        "/project/track_count" => handle_track_count(&msg, sender_addr),
        "/project/tempo/get"   => handle_get_tempo(&msg, sender_addr),
        "/project/tempo/set"   => handle_set_tempo(&msg, sender_addr),

        // Track operations
        "/track/scan"        => handle_scan_track(&msg, sender_addr),
        "/track/name/get"    => handle_get_track_name(&msg, sender_addr),
        "/track/name/set"    => handle_set_track_name(&msg, sender_addr),
        "/track/volume/get"  => handle_get_track_volume(&msg, sender_addr),
        "/track/volume/set"  => handle_set_track_volume(&msg, sender_addr),
        "/track/pan/get"     => handle_get_track_pan(&msg, sender_addr),
        "/track/pan/set"     => handle_set_track_pan(&msg, sender_addr),

        // FX operations
        "/fx/add"          => handle_add_fx(&msg, sender_addr),
        "/fx/remove"       => handle_remove_fx(&msg, sender_addr),
        "/fx/param/get"    => handle_get_fx_param(&msg, sender_addr),
        "/fx/param/set"    => handle_set_fx_param(&msg, sender_addr),
        "/fx/params/scan"  => handle_scan_fx_params(&msg, sender_addr),

        // MIDI operations
        "/note" => handle_play_note(&msg, sender_addr),

        _ => {
            show_console_msg(&format!(
                "[renardo-fresh] Unknown route: {}\n",
                msg.addr
            ));
        }
    }
}
