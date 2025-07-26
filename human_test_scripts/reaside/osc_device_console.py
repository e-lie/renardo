#!/usr/bin/env python3
"""
Console-based OSC device for REAPER testing.
Ports: 8766 (send to REAPER) / 8767 (receive from REAPER)
Based on Default.ReaperOSC patterns.
"""

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
        self.running = True
        
        # Setup OSC message handlers
        self.setup_osc_handlers()
        
        # Start OSC server
        self.start_osc_server()
        
        print(f"Console OSC Device started:")
        print(f"  Sending to REAPER: {self.reaper_host}:{self.send_port}")
        print(f"  Receiving from REAPER: {self.reaper_host}:{self.receive_port}")
        print(f"  Configure REAPER OSC device: localhost:{self.receive_port} -> localhost:{self.send_port}")
        print()
        
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
        
        # FX parameter feedback (for testing)
        self.dispatcher.map("/track/*/fx/*/fxparam/*/value", self.handle_fx_param)
        self.dispatcher.map("/fx/*/fxparam/*/value", self.handle_fx_param)
        self.dispatcher.map("/fxparam/*/value", self.handle_fx_param)
        
        # Catch-all for debugging
        self.dispatcher.map("/*", self.handle_any_message)
        
    def handle_track_volume(self, address, *args):
        """Handle track volume feedback from REAPER."""
        try:
            track_num = int(address.split('/')[2])
            if len(args) > 0:
                volume = float(args[0])
                print(f"← Volume feedback: track {track_num} = {volume:.3f}")
                if track_num == self.current_track:
                    self.current_volume = volume
        except Exception as e:
            print(f"Error handling volume: {e}")
            
    def handle_track_volume_str(self, address, *args):
        """Handle track volume string feedback."""
        try:
            track_num = int(address.split('/')[2])
            if len(args) > 0:
                volume_str = args[0]
                print(f"← Volume string: track {track_num} = {volume_str}")
        except Exception as e:
            print(f"Error handling volume string: {e}")
            
    def handle_track_name(self, address, *args):
        """Handle track name feedback."""
        try:
            track_num = int(address.split('/')[2])
            if len(args) > 0:
                name = str(args[0])
                print(f"← Track name: track {track_num} = '{name}'")
                if track_num == self.current_track:
                    self.track_name = name
        except Exception as e:
            print(f"Error handling track name: {e}")
            
    def handle_track_mute(self, address, *args):
        """Handle track mute feedback."""
        try:
            track_num = int(address.split('/')[2])
            if len(args) > 0:
                muted = bool(args[0])
                print(f"← Mute feedback: track {track_num} = {muted}")
                if track_num == self.current_track:
                    self.is_muted = muted
        except Exception as e:
            print(f"Error handling mute: {e}")
            
    def handle_track_select(self, address, *args):
        """Handle track select feedback."""
        print(f"← Track select: {address} {args}")
        
    def handle_fx_param(self, address, *args):
        """Handle FX parameter feedback."""
        print(f"← FX PARAM: {address} {args}")
        
    def handle_any_message(self, address, *args):
        """Debug handler for all messages."""
        # Filter out common messages to reduce spam
        if not any(x in address for x in ['/volume', '/name', '/mute']):
            print(f"← OSC: {address} {args}")
        
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
            
    def send_track_select(self, track_num):
        """Select a track."""
        try:
            self.client.send_message(f"/track/{track_num}/select", 1)
            print(f"→ Sent: /track/{track_num}/select 1")
            self.current_track = track_num
        except Exception as e:
            print(f"Error sending track select: {e}")
            
    def send_volume(self, track_num, volume):
        """Set track volume."""
        try:
            self.client.send_message(f"/track/{track_num}/volume", volume)
            print(f"→ Sent: /track/{track_num}/volume {volume:.3f}")
        except Exception as e:
            print(f"Error sending volume: {e}")
            
    def send_mute(self, track_num, muted):
        """Set track mute."""
        try:
            self.client.send_message(f"/track/{track_num}/mute", 1 if muted else 0)
            print(f"→ Sent: /track/{track_num}/mute {1 if muted else 0}")
        except Exception as e:
            print(f"Error sending mute: {e}")
            
    def send_fx_param(self, track_num, fx_num, param_num, value):
        """Send FX parameter change."""
        try:
            addr = f"/track/{track_num}/fx/{fx_num}/fxparam/{param_num}/value"
            self.client.send_message(addr, value)
            print(f"→ Sent: {addr} {value:.3f}")
        except Exception as e:
            print(f"Error sending FX param: {e}")
            
    def run_console(self):
        """Run console interface."""
        print("\n=== Commands ===")
        print("t<num>     - Select track (e.g., t1, t2)")
        print("v<value>   - Set volume 0.0-1.0 (e.g., v0.5)")
        print("m          - Toggle mute")
        print("f<fx><param><value> - Set FX param (e.g., f011.0)")
        print("p23<value> - Set param 3 of fx 2 (e.g., p230.5)")
        print("help       - Show commands")
        print("quit       - Exit")
        print()
        
        while self.running:
            try:
                cmd = input(f"[Track {self.current_track}] > ").strip().lower()
                
                if cmd == "quit" or cmd == "q":
                    break
                elif cmd == "help" or cmd == "h":
                    print("t<num> = select track, v<val> = volume, m = mute, f<fx><param><val> = fx param, p23<val> = fx2 param3")
                elif cmd.startswith("t") and len(cmd) > 1:
                    track_num = int(cmd[1:])
                    self.send_track_select(track_num)
                elif cmd.startswith("v") and len(cmd) > 1:
                    volume = float(cmd[1:])
                    self.send_volume(self.current_track, volume)
                elif cmd == "m":
                    self.is_muted = not self.is_muted
                    self.send_mute(self.current_track, self.is_muted)
                elif cmd.startswith("p23") and len(cmd) > 3:
                    # Special command: p23<value> = fx 2, param 3
                    value = float(cmd[3:])
                    self.send_fx_param(self.current_track, 2, 3, value)
                elif cmd.startswith("f") and len(cmd) >= 4:
                    # Parse f<fx><param><value> format
                    fx_num = int(cmd[1])
                    param_num = int(cmd[2])
                    value = float(cmd[3:])
                    self.send_fx_param(self.current_track, fx_num, param_num, value)
                elif cmd == "":
                    continue
                else:
                    print("Unknown command. Type 'help' for commands.")
                    
            except KeyboardInterrupt:
                break
            except ValueError as e:
                print(f"Invalid input: {e}")
            except Exception as e:
                print(f"Error: {e}")
                
        self.running = False
        print("\nShutting down...")
        self.stop_osc_server()

if __name__ == "__main__":
    print("Starting REAPER OSC Device (Console)")
    print("Configure REAPER OSC device with:")
    print("  Device local port: 8767")
    print("  Device sends to: 127.0.0.1:8766")
    print("  Pattern config: Default.ReaperOSC")
    print()
    
    device = ReaperOSCDevice()
    device.run_console()