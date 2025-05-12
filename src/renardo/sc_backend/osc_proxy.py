from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
import threading
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class OSCEvent:
    """Represents an OSC event with its timestamp."""
    address: str
    args: List[Any]
    timestamp: float


class OSCProxy:
    """Proxy that intercepts and records OSC messages."""

    def __init__(self, listen_port: int = 57120, forward_port: int = 57110,
                 ignored_addresses = ["/g_freeall", "/dumpOSC"]):
        """
        Initialize the OSC proxy.

        Args:
            listen_port: Port to listen for incoming messages
            forward_port: Port to forward messages to SuperCollider
        """
        self.listen_port = listen_port
        self.forward_port = forward_port
        self.events: List[OSCEvent] = []
        self.start_time: Optional[float] = None
        self.ignored_addresses = ignored_addresses

        # Client for forwarding to SuperCollider
        self.client = udp_client.SimpleUDPClient("127.0.0.1", forward_port)

        # Dispatcher configuration
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.set_default_handler(self._handle_message)

        # OSC server
        self.server = osc_server.ThreadingOSCUDPServer(
            ("127.0.0.1", listen_port),
            self.dispatcher
        )

        # Server thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

    def start(self):
        """Start the proxy."""
        self.events.clear()
        self.start_time = None
        self.server_thread.start()
        print(f"OSC Proxy listening on port {self.listen_port} and forwarding to {self.forward_port}")

    def stop(self):
        """Stop the proxy."""
        self.server.shutdown()
        self.server_thread.join()

    def _handle_message(self, address: str, *args):
        """Handle received OSC messages."""

        # ignore message at start of session
        # ie sent when executing (from renardo.runtime import *)
        if address in self.ignored_addresses:
            return None

        current_time = time.time()

        # Set start time on first event
        if self.start_time is None:
            self.start_time = current_time

        # Calculate time relative to first event
        relative_time = current_time - self.start_time

        # Record the event
        event = OSCEvent(address, list(args), relative_time)
        self.events.append(event)

        # Print OSC message
        args_str = ' '.join(str(arg) for arg in args)
        print(f"[{relative_time:.3f}] {address} {args_str}")

        # Forward message to SuperCollider
        self.client.send_message(address, args)

    def save_events(self, prefix: str = "osc_events"):
        """
        Save events to a JSON file in /tmp with timestamp.

        Args:
            prefix: Prefix for the filename (default: "osc_events")
        """
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/{prefix}_{timestamp}.json"

        output_path = Path(filename)

        with open(output_path, 'w') as f:
            events_dict = [asdict(event) for event in self.events]
            json.dump(events_dict, f, indent=2)

        print(f"Events saved to {filename}")
        return filename

    def load_events(self, filename: str) -> List[OSCEvent]:
        """Load events from a JSON file."""
        with open(filename, 'r') as f:
            events_dict = json.load(f)
            return [OSCEvent(**event) for event in events_dict]

    def clear(self):
        """Clear all recorded events."""
        self.events.clear()
        self.start_time = None
        print("Events cleared")


# Standalone usage example
if __name__ == "__main__":
    proxy = OSCProxy()
    proxy.start()

    try:
        print("Press Ctrl+C to stop and save events")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        saved_file = proxy.save_events()
        proxy.stop()
        print("\nProxy stopped")