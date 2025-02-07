import pytest
from pathlib import Path
import json
import time
from datetime import datetime
import os
from dataclasses import asdict
from renardo_sc_backend.osc_proxy import OSCProxy
import importlib

# Configuration
RECORD_MODE = os.environ.get('RENARDO_TEST_RECORD', 'False').lower() == 'true'
TEST_DATA_DIR = Path('osc_test_recording')
TIMING_TOLERANCE = 0.1

class TestSessionManager:
    """Manages the test session including OSC proxy and runtime initialization."""
    
    def __init__(self):
        self.session_dir = None
        self.proxy = None
        self.runtime = None
        self._initialize_session_directory()
        self._initialize_osc_proxy()
        self._initialize_runtime()
        
    def _initialize_session_directory(self):
        """Initialize the session directory for recordings."""
        if RECORD_MODE:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_dir = TEST_DATA_DIR / f"session_{timestamp}"
            self.session_dir.mkdir(parents=True, exist_ok=True)
        else:
            if TEST_DATA_DIR.exists():
                sessions = sorted(TEST_DATA_DIR.glob("session_*"))
                if sessions:
                    self.session_dir = sessions[-1]
                    
    def _initialize_osc_proxy(self):
        """Initialize and start the OSC proxy."""
        self.proxy = OSCProxy(listen_port=57120, forward_port=57110)
        self.proxy.start()
        print("OSC Proxy started and ready")
        time.sleep(1)  # Give proxy time to start
        
    def _initialize_runtime(self):
        """Initialize the Renardo runtime after proxy is ready."""
        print("Initializing Renardo runtime...")
        # Import runtime after proxy is ready
        self.runtime = importlib.import_module('renardo_lib.runtime')
        # Make runtime objects available in global namespace
        globals().update({name: getattr(self.runtime, name) 
                         for name in dir(self.runtime) 
                         if not name.startswith('_')})
        # Wait for initialization messages
        time.sleep(1)
        self.proxy.clear()  # Clear initialization messages
        print("Runtime initialized and connected to proxy")
        
    def get_recording_path(self, test_name: str) -> Path:
        """Get path for recording or comparing a test."""
        if not self.session_dir:
            raise RuntimeError("No session directory available")
        return self.session_dir / f"{test_name}.json"
    
    def start_recording(self):
        """Start recording a new test case."""
        self.proxy.clear()
        
    def stop_recording(self, test_name: str):
        """Stop recording and save or verify events."""
        recording_path = self.get_recording_path(test_name)
        
        if RECORD_MODE:
            # Save recorded events
            with open(recording_path, 'w') as f:
                events_dict = [asdict(event) for event in self.proxy.events]
                json.dump(events_dict, f, indent=2)
            print(f"Recorded test case '{test_name}' to {recording_path}")
        else:
            # Compare with recorded events
            with open(recording_path) as f:
                expected_events = json.load(f)
            self._compare_events(self.proxy.events, expected_events)
    
    def _compare_events(self, actual_events, expected_events):
        """Compare two sequences of OSC events."""
        assert len(actual_events) == len(expected_events), \
            f"Incorrect number of events. Expected: {len(expected_events)}, Got: {len(actual_events)}"

        for actual, expected in zip(actual_events, expected_events):
            assert actual.address == expected["address"], \
                f"Incorrect OSC address. Expected: {expected['address']}, Got: {actual.address}"
            
            assert actual.args == expected["args"], \
                f"Incorrect arguments. Expected: {expected['args']}, Got: {actual.args}"
            
            assert abs(actual.timestamp - expected["timestamp"]) <= TIMING_TOLERANCE, \
                f"Incorrect timing. Expected: {expected['timestamp']}, Got: {actual.timestamp}"
    
    def cleanup(self):
        """Cleanup resources."""
        if self.proxy:
            self.proxy.stop()

@pytest.fixture(scope="session")
def test_session(request):
    """Session-level fixture providing test session management."""
    manager = TestSessionManager()
    
    def cleanup():
        manager.cleanup()
    request.addfinalizer(cleanup)
    
    return manager

def run_test_case(test_name: str, test_session, test_func):
    """Run a test case with proper recording/verification."""
    test_session.start_recording()
    
    # Run the test function
    test_func()
    
    # Allow time for events to be processed
    time.sleep(0.5)
    
    test_session.stop_recording(test_name)

def test_blip_1(test_session):
    """Test basic blip pattern."""
    def test_case():
        b1 = Player()
        b1 >> blip([0,2,4,5,6])
        Clock.set_time(0)
        time.sleep(2)
        Clock.clear()
    
    run_test_case('test_blip_1', test_session, test_case)

def test_blip_2(test_session):
    """Test another blip pattern."""
    def test_case():
        b1 = Player()
        b1 >> blip([0,1,2,3])
        Clock.set_time(0)
        time.sleep(2)
        Clock.clear()
    
    run_test_case('test_blip_2', test_session, test_case)

if __name__ == "__main__":
    print("""
Run tests in record mode:
    RENARDO_TEST_RECORD=true pytest test_functional_renardo_sc.py -v

Run tests in verify mode:
    pytest test_functional_renardo_sc.py -v
    """)