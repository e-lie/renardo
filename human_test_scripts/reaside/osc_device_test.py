#!/usr/bin/env python3
"""
Independent OSC device for REAPER testing.
Ports: 8766 (send to REAPER) / 8767 (receive from REAPER)
Based on Default.ReaperOSC patterns.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import sys

try:
    from pythonosc import udp_client, dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer
except ImportError:
    print("Error: python-osc library required")
    print("Install with: pip install python-osc")
    sys.exit(1)

class ReaperOSCDevice:
    def __init__(self):
        # OSC configuration
        self.reaper_host = "127.0.0.1"
        self.send_port = 8766      # Send to REAPER on 8766
        self.receive_port = 8767   # Receive from REAPER on 8767
        
        # OSC client for sending to REAPER
        self.client = udp_client.SimpleUDPClient(self.reaper_host, self.send_port)
        
        # OSC server for receiving from REAPER
        self.dispatcher = dispatcher.Dispatcher()
        self.server = None
        self.server_thread = None
        
        # Device state
        self.current_track = 1
        self.current_volume = 0.5
        self.track_name = "Track 1"
        self.is_muted = False
        
        # Setup OSC message handlers
        self.setup_osc_handlers()
        
        # Create GUI
        self.setup_gui()
        
        # Start OSC server
        self.start_osc_server()
        
        print(f"OSC Device started:")
        print(f"  Sending to REAPER: {self.reaper_host}:{self.send_port}")
        print(f"  Receiving from REAPER: {self.reaper_host}:{self.receive_port}")
        print(f"  Configure REAPER OSC device: localhost:{self.receive_port} -> localhost:{self.send_port}")
        
    def setup_osc_handlers(self):
        """Setup OSC message handlers based on Default.ReaperOSC patterns."""
        # Track volume feedback
        self.dispatcher.map("/track/*/volume", self.handle_track_volume)
        self.dispatcher.map("/track/*/volume/str", self.handle_track_volume_str)
        
        # Track name feedback
        self.dispatcher.map("/track/*/name", self.handle_track_name)
        
        # Track mute feedback
        self.dispatcher.map("/track/*/mute", self.handle_track_mute)
        
        # Track select feedback
        self.dispatcher.map("/track/*/select", self.handle_track_select)
        
        # Device track feedback
        self.dispatcher.map("/device/track/select", self.handle_device_track_select)
        
        # Catch-all for debugging
        self.dispatcher.map("/*", self.handle_any_message)
        
    def handle_track_volume(self, address, *args):
        """Handle track volume feedback from REAPER."""
        try:
            track_num = int(address.split('/')[2])
            if track_num == self.current_track and len(args) > 0:
                volume = float(args[0])
                self.current_volume = volume
                self.root.after(0, self.update_volume_display)
                print(f"Received volume: track {track_num} = {volume:.3f}")
        except Exception as e:
            print(f"Error handling volume: {e}")
            
    def handle_track_volume_str(self, address, *args):
        """Handle track volume string feedback."""
        try:
            track_num = int(address.split('/')[2])
            if track_num == self.current_track and len(args) > 0:
                volume_str = args[0]
                print(f"Received volume string: track {track_num} = {volume_str}")
        except Exception as e:
            print(f"Error handling volume string: {e}")
            
    def handle_track_name(self, address, *args):
        """Handle track name feedback."""
        try:
            track_num = int(address.split('/')[2])
            if track_num == self.current_track and len(args) > 0:
                name = str(args[0])
                self.track_name = name
                self.root.after(0, self.update_track_display)
                print(f"Received track name: track {track_num} = {name}")
        except Exception as e:
            print(f"Error handling track name: {e}")
            
    def handle_track_mute(self, address, *args):
        """Handle track mute feedback."""
        try:
            track_num = int(address.split('/')[2])
            if track_num == self.current_track and len(args) > 0:
                muted = bool(args[0])
                self.is_muted = muted
                self.root.after(0, self.update_mute_display)
                print(f"Received mute: track {track_num} = {muted}")
        except Exception as e:
            print(f"Error handling mute: {e}")
            
    def handle_track_select(self, address, *args):
        """Handle track select feedback."""
        print(f"Track select: {address} {args}")
        
    def handle_device_track_select(self, address, *args):
        """Handle device track select feedback."""
        print(f"Device track select: {address} {args}")
        
    def handle_any_message(self, address, *args):
        """Debug handler for all messages."""
        print(f"OSC: {address} {args}")
        
    def start_osc_server(self):
        """Start the OSC server to receive messages from REAPER."""
        try:
            self.server = ThreadingOSCUDPServer(
                (self.reaper_host, self.receive_port), 
                self.dispatcher
            )
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            print(f"OSC server started on port {self.receive_port}")
        except Exception as e:
            print(f"Failed to start OSC server: {e}")
            
    def stop_osc_server(self):
        """Stop the OSC server."""
        if self.server:
            self.server.shutdown()
            
    def setup_gui(self):
        """Create the Tkinter GUI."""
        self.root = tk.Tk()
        self.root.title("REAPER OSC Device Test")
        self.root.geometry("400x300")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Track info
        track_frame = ttk.Frame(self.root)
        track_frame.pack(pady=10)
        
        ttk.Label(track_frame, text="Track:").pack(side=tk.LEFT)
        self.track_label = ttk.Label(track_frame, text=f"{self.current_track}: {self.track_name}", 
                                   font=("Arial", 12, "bold"))
        self.track_label.pack(side=tk.LEFT, padx=10)
        
        # Track navigation
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(pady=10)
        
        self.prev_btn = ttk.Button(nav_frame, text="← Prev Track", command=self.prev_track)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(nav_frame, text="Next Track →", command=self.next_track)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # Volume control
        vol_frame = ttk.Frame(self.root)
        vol_frame.pack(pady=20, fill=tk.X, padx=20)
        
        ttk.Label(vol_frame, text="Volume:").pack(anchor=tk.W)
        
        self.volume_var = tk.DoubleVar(value=self.current_volume)
        self.volume_scale = ttk.Scale(vol_frame, from_=0.0, to=1.0, 
                                    variable=self.volume_var, orient=tk.HORIZONTAL,
                                    command=self.on_volume_change)
        self.volume_scale.pack(fill=tk.X, pady=5)
        
        self.volume_label = ttk.Label(vol_frame, text=f"{self.current_volume:.3f}")
        self.volume_label.pack(anchor=tk.W)
        
        # Mute button
        self.mute_var = tk.BooleanVar(value=self.is_muted)
        self.mute_btn = ttk.Checkbutton(vol_frame, text="Mute", variable=self.mute_var,
                                      command=self.on_mute_change)
        self.mute_btn.pack(anchor=tk.W, pady=5)
        
        # Status
        status_frame = ttk.Frame(self.root)
        status_frame.pack(pady=10, fill=tk.X, padx=20)
        
        ttk.Label(status_frame, text="OSC Status:").pack(anchor=tk.W)
        self.status_label = ttk.Label(status_frame, text=f"Send: {self.send_port}, Receive: {self.receive_port}")
        self.status_label.pack(anchor=tk.W)
        
        # Request track info button
        info_btn = ttk.Button(self.root, text="Request Track Info", command=self.request_track_info)
        info_btn.pack(pady=10)
        
    def prev_track(self):
        """Switch to previous track."""
        if self.current_track > 1:
            self.current_track -= 1
            self.switch_to_track(self.current_track)
            
    def next_track(self):
        """Switch to next track."""
        self.current_track += 1
        self.switch_to_track(self.current_track)
        
    def switch_to_track(self, track_num):
        """Switch to specified track and request info."""
        print(f"Switching to track {track_num}")
        
        # Send track select message
        try:
            self.client.send_message(f"/track/{track_num}/select", 1)
            print(f"Sent: /track/{track_num}/select 1")
        except Exception as e:
            print(f"Error sending track select: {e}")
            
        # Request track info
        self.request_track_info()
        
    def request_track_info(self):
        """Request current track information from REAPER."""
        track_num = self.current_track
        
        try:
            # Request track name, volume, mute status
            # Note: These might not work if REAPER doesn't send feedback automatically
            # In a real implementation, you'd need proper query messages
            
            print(f"Requesting info for track {track_num}")
            
            # Update display with current track
            self.update_track_display()
            
        except Exception as e:
            print(f"Error requesting track info: {e}")
            
    def on_volume_change(self, value):
        """Handle volume slider change."""
        volume = float(value)
        self.current_volume = volume
        
        # Send volume change to REAPER
        try:
            self.client.send_message(f"/track/{self.current_track}/volume", volume)
            print(f"Sent: /track/{self.current_track}/volume {volume:.3f}")
        except Exception as e:
            print(f"Error sending volume: {e}")
            
        # Update display
        self.volume_label.config(text=f"{volume:.3f}")
        
    def on_mute_change(self):
        """Handle mute button change."""
        muted = self.mute_var.get()
        self.is_muted = muted
        
        # Send mute change to REAPER
        try:
            self.client.send_message(f"/track/{self.current_track}/mute", 1 if muted else 0)
            print(f"Sent: /track/{self.current_track}/mute {1 if muted else 0}")
        except Exception as e:
            print(f"Error sending mute: {e}")
            
    def update_volume_display(self):
        """Update volume display from received OSC."""
        self.volume_var.set(self.current_volume)
        self.volume_label.config(text=f"{self.current_volume:.3f}")
        
    def update_track_display(self):
        """Update track display."""
        self.track_label.config(text=f"{self.current_track}: {self.track_name}")
        
    def update_mute_display(self):
        """Update mute display from received OSC."""
        self.mute_var.set(self.is_muted)
        
    def on_closing(self):
        """Handle window closing."""
        print("Shutting down OSC device...")
        self.stop_osc_server()
        self.root.destroy()
        
    def run(self):
        """Run the GUI main loop."""
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting REAPER OSC Device Test")
    print("Configure REAPER OSC device with:")
    print("  Remote device sends to: 127.0.0.1:8766")
    print("  Remote device receives from: 127.0.0.1:8767")
    print("  Pattern config: Default.ReaperOSC")
    print()
    
    device = ReaperOSCDevice()
    device.run()