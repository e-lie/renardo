#!/usr/bin/env python3
"""Infinite melody demo using the new MIDI note system."""

import time
import sys
import os
import threading
import random

# Add the renardo package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.rust_osc_client import RustOscClient

class MelodyPlayer:
    def __init__(self):
        self.client = RustOscClient()
        self.running = False
        self.thread = None
        
        # Define some melodic patterns
        self.melodies = {
            "pentatonic": [60, 62, 65, 67, 69],  # C major pentatonic
            "minor": [60, 62, 63, 65, 67, 68, 70],  # C minor scale
            "major": [60, 62, 64, 65, 67, 69, 71],  # C major scale
            "blues": [60, 63, 65, 66, 67, 70],  # C blues scale
            "dorian": [60, 62, 63, 65, 67, 69, 70],  # C dorian
        }
        
        self.current_melody = "pentatonic"
        self.current_channel = 1
        
    def start(self):
        """Start the infinite melody loop."""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._melody_loop)
        self.thread.daemon = True
        self.thread.start()
        print(f"🎵 Started infinite melody on channel {self.current_channel}")
        print("Press Ctrl+C to stop")
        
    def stop(self):
        """Stop the melody loop."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print("🛑 Melody stopped")
        
    def change_melody(self, melody_name):
        """Change the melody pattern."""
        if melody_name in self.melodies:
            self.current_melody = melody_name
            print(f"🎼 Changed to {melody_name} melody")
        else:
            print(f"❌ Unknown melody: {melody_name}")
            
    def change_channel(self, channel):
        """Change MIDI channel (1-16)."""
        if 1 <= channel <= 16:
            self.current_channel = channel
            print(f"📻 Changed to channel {channel}")
        else:
            print(f"❌ Invalid channel: {channel} (must be 1-16)")
            
    def _melody_loop(self):
        """Main melody loop - 4Hz (250ms per note)."""
        note_duration = 50  # Slightly shorter than 250ms to avoid overlap
        
        while self.running:
            try:
                melody = self.melodies[self.current_melody]
                
                for note in melody:
                    if not self.running:
                        break
                        
                    # Add some musical variation
                    velocity = random.randint(80, 120)
                    
                    # Occasionally play octave higher
                    if random.random() < 0.1:
                        note += 12
                        
                    # Play the note
                    success = self.client.play_note(
                        midi_channel=self.current_channel,
                        midi_note=note,
                        velocity=velocity,
                        duration_ms=note_duration
                    )
                    
                    if not success:
                        print("❌ Failed to play note - is REAPER running?")
                        self.running = False
                        break
                        
                    # 4Hz = 250ms per note
                    time.sleep(0.05)
                    
            except Exception as e:
                print(f"❌ Error in melody loop: {e}")
                self.running = False
                break
                
    def interactive_mode(self):
        """Interactive mode with keyboard commands."""
        print("\n🎹 Interactive Melody Player")
        print("Commands:")
        print("  1-5: Change melody (1=pentatonic, 2=minor, 3=major, 4=blues, 5=dorian)")
        print("  c1-c16: Change channel (e.g., 'c1' for channel 1)")
        print("  s: Start/restart melody")
        print("  q: Quit")
        print()
        
        melody_names = list(self.melodies.keys())
        
        while True:
            try:
                cmd = input(f"[{self.current_melody} ch{self.current_channel}] > ").strip().lower()
                
                if cmd == 'q':
                    break
                elif cmd == 's':
                    self.stop()
                    time.sleep(0.1)
                    self.start()
                elif cmd in ['1', '2', '3', '4', '5']:
                    idx = int(cmd) - 1
                    if idx < len(melody_names):
                        self.change_melody(melody_names[idx])
                elif cmd.startswith('c') and len(cmd) > 1:
                    try:
                        channel = int(cmd[1:])
                        self.change_channel(channel)
                    except ValueError:
                        print("❌ Invalid channel format. Use c1, c2, etc.")
                else:
                    print("❌ Unknown command")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break

def demo_sequences():
    """Run some pre-programmed demo sequences."""
    player = MelodyPlayer()
    
    try:
        print("🎵 MIDI Melody Demo - Sequence Mode")
        print("=" * 50)
        
        sequences = [
            ("pentatonic", 1, 8),  # melody, channel, duration
            ("blues", 1, 8),
            ("minor", 2, 8),
            ("major", 1, 8),
            ("dorian", 2, 6),
        ]
        
        for melody, channel, duration in sequences:
            print(f"\n🎼 Playing {melody} on channel {channel} for {duration} seconds...")
            player.change_melody(melody)
            player.change_channel(channel)
            player.start()
            time.sleep(duration)
            player.stop()
            time.sleep(0.5)  # Brief pause between sequences
            
        print("\n🎉 Demo complete!")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted")
    finally:
        player.stop()
        player.client.close()

def main():
    """Main function with mode selection."""
    print("🎵 MIDI Melody Player")
    print("Choose mode:")
    print("1. Interactive mode (control with keyboard)")
    print("2. Demo sequences")
    print("3. Simple infinite loop")
    
    try:
        choice = input("Mode (1-3): ").strip()
        
        if choice == '1':
            player = MelodyPlayer()
            try:
                player.start()
                player.interactive_mode()
            finally:
                player.stop()
                player.client.close()
                
        elif choice == '2':
            demo_sequences()
            
        elif choice == '3':
            player = MelodyPlayer()
            try:
                player.start()
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopped")
            finally:
                player.stop()
                player.client.close()
                
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()