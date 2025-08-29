/*! MIDI note management with automatic note-off scheduling */

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use std::thread;

use crate::reaper::api::*;

/// Represents an active MIDI note
#[derive(Debug, Clone)]
struct ActiveNote {
    midi_channel: u8,
    note: u8,
    velocity: u8,
    start_time: Instant,
    duration_ms: u64,
}

/// Global note manager instance
static mut NOTE_MANAGER: Option<Arc<Mutex<NoteManager>>> = None;

/// MIDI note manager that handles automatic note-off messages
pub struct NoteManager {
    active_notes: HashMap<(u8, u8), ActiveNote>, // Key: (midi_channel, note)
}

impl NoteManager {
    pub fn new() -> Self {
        NoteManager {
            active_notes: HashMap::new(),
        }
    }

    /// Play a MIDI note with automatic note-off handling
    pub fn play_note(&mut self, midi_channel: u8, note: u8, velocity: u8, duration_ms: u64) {
        show_console_msg(&format!("[renardo-ext] Playing note {} on ch{} vel{} dur{}ms\n", 
                                note, midi_channel, velocity, duration_ms));

        let note_key = (midi_channel, note);
        
        // If note is already playing, stop it immediately
        if let Some(active_note) = self.active_notes.get(&note_key) {
            show_console_msg(&format!("[renardo-ext] Stopping existing note {} on ch{}\n", 
                                    note, midi_channel));
            self.send_note_off(active_note.midi_channel, note);
        }

        // Send note-on immediately
        self.send_note_on(midi_channel, note, velocity);

        // Store the active note
        let active_note = ActiveNote {
            midi_channel,
            note,
            velocity,
            start_time: Instant::now(),
            duration_ms,
        };
        self.active_notes.insert(note_key, active_note.clone());

        // Schedule note-off in a separate thread
        let manager_clone = get_note_manager();
        thread::spawn(move || {
            thread::sleep(Duration::from_millis(duration_ms));
            
            if let Ok(mut manager) = manager_clone.lock() {
                let note_key = (midi_channel, note);
                
                // Check if this is still the same note (not replaced by a newer one)
                if let Some(current_note) = manager.active_notes.get(&note_key) {
                    if current_note.start_time == active_note.start_time {
                        show_console_msg(&format!("[renardo-ext] Auto note-off {} on ch{}\n", 
                                                note, midi_channel));
                        manager.send_note_off(midi_channel, note);
                        manager.active_notes.remove(&note_key);
                    }
                }
            }
        });
    }

    /// Send MIDI note-on message
    fn send_note_on(&self, channel: u8, note: u8, velocity: u8) {
        // MIDI note-on: status byte (0x90 | channel), note, velocity
        let status = 0x90 | (channel & 0x0F);
        let midi_msg = [status, note, velocity];
        
        unsafe {
            if let Some(stuff_midi) = STUFF_MIDI_MESSAGE {
                stuff_midi(0, midi_msg.as_ptr(), midi_msg.len() as i32);
            }
        }
    }

    /// Send MIDI note-off message
    fn send_note_off(&self, channel: u8, note: u8) {
        // MIDI note-off: status byte (0x80 | channel), note, velocity 0
        let status = 0x80 | (channel & 0x0F);
        let midi_msg = [status, note, 0];
        
        unsafe {
            if let Some(stuff_midi) = STUFF_MIDI_MESSAGE {
                stuff_midi(0, midi_msg.as_ptr(), midi_msg.len() as i32);
            }
        }
    }

    /// Stop all notes on a specific MIDI channel
    pub fn stop_all_notes_on_channel(&mut self, midi_channel: u8) {
        let mut notes_to_stop = Vec::new();
        
        for ((ch, note), _active_note) in &self.active_notes {
            if *ch == midi_channel {
                notes_to_stop.push(*note);
            }
        }
        
        for note in notes_to_stop {
            self.send_note_off(midi_channel, note);
            self.active_notes.remove(&(midi_channel, note));
        }
    }

    /// Get count of active notes
    pub fn active_note_count(&self) -> usize {
        self.active_notes.len()
    }
}

/// Get or initialize the global note manager
pub fn get_note_manager() -> Arc<Mutex<NoteManager>> {
    unsafe {
        if NOTE_MANAGER.is_none() {
            NOTE_MANAGER = Some(Arc::new(Mutex::new(NoteManager::new())));
        }
        NOTE_MANAGER.as_ref().unwrap().clone()
    }
}

/// Initialize the note manager (called from plugin init)
pub fn init_note_manager() {
    let _manager = get_note_manager();
    show_console_msg("[renardo-ext] MIDI note manager initialized\n");
}