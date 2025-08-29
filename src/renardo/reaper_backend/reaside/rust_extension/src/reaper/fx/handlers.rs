/*! REAPER FX OSC handlers */

use std::net::SocketAddr;
use rosc::OscMessage;

use crate::reaper::api::show_console_msg;

/// Handle OSC route: /fx/add (placeholder for future implementation)
pub fn handle_add_fx(msg: &OscMessage, sender_addr: SocketAddr) {
    show_console_msg("[renardo-ext] FX operations not yet implemented\n");
}

/// Handle OSC route: /fx/remove (placeholder for future implementation)
pub fn handle_remove_fx(msg: &OscMessage, sender_addr: SocketAddr) {
    show_console_msg("[renardo-ext] FX operations not yet implemented\n");
}

/// Handle OSC route: /fx/param/get (placeholder for future implementation)
pub fn handle_get_fx_param(msg: &OscMessage, sender_addr: SocketAddr) {
    show_console_msg("[renardo-ext] FX parameter operations not yet implemented\n");
}

/// Handle OSC route: /fx/param/set (placeholder for future implementation)
pub fn handle_set_fx_param(msg: &OscMessage, sender_addr: SocketAddr) {
    show_console_msg("[renardo-ext] FX parameter operations not yet implemented\n");
}