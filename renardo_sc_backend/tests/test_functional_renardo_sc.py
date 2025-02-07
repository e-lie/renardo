import pytest
from pathlib import Path
import json
import time
from datetime import datetime
import os
from dataclasses import asdict
from renardo_sc_backend.osc_proxy import OSCProxy
import importlib
from enum import Enum, auto

class TestMode(Enum):
    RECORD = auto()
    VERIFY = auto()
    PASS_THROUGH = auto()

# Configuration
TEST_MODE = os.environ.get('RENARDO_TEST_MODE', 'verify').lower()
if TEST_MODE == 'record':
    MODE = TestMode.RECORD
elif TEST_MODE == 'pass_through':
    MODE = TestMode.PASS_THROUGH
else:
    MODE = TestMode.VERIFY

TEST_DATA_DIR = Path('osc_test_recording')
TIMING_TOLERANCE = 0.1

class TestSessionManager:
    """Manages the test session including OSC proxy and runtime initialization."""
    
    def __init__(self):
        self.session_dir = None
        self.proxy = None
        self.runtime = None
        self._initialize_session_directory()
        if MODE != TestMode.PASS_THROUGH:
            self._initialize_osc_proxy()
        self._initialize_runtime()
        
    def _initialize_session_directory(self):
        """Initialize the session directory for recordings."""
        if MODE == TestMode.RECORD:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_dir = TEST_DATA_DIR / f"session_{timestamp}"
            self.session_dir.mkdir(parents=True, exist_ok=True)
        elif MODE == TestMode.VERIFY:
            if TEST_DATA_DIR.exists():
                sessions = sorted(TEST_DATA_DIR.glob("session_*"))
                if sessions:
                    self.session_dir = sessions[-1]
                    
    def _initialize_osc_proxy(self):
        """Initialize and start the OSC proxy."""
        self.proxy = OSCProxy(listen_port=57110, forward_port=57120)
        self.proxy.start()
        print("OSC Proxy started and ready")
        time.sleep(1)  # Give proxy time to start
        
    def _initialize_runtime(self):
        """Initialize the Renardo runtime."""
        print("Initializing Renardo runtime...")
        # Import runtime
        self.runtime = importlib.import_module('renardo_lib.runtime')
        # Make runtime objects available in global namespace
        globals().update({name: getattr(self.runtime, name) 
                         for name in dir(self.runtime) 
                         if not name.startswith('_')})
        # Wait for initialization messages
        time.sleep(1)
        if self.proxy:
            self.proxy.clear()  # Clear initialization messages
        print("Runtime initialized")
        
    def get_recording_path(self, test_name: str) -> Path:
        """Get path for recording or comparing a test."""
        if not self.session_dir:
            raise RuntimeError("No session directory available")
        return self.session_dir / f"{test_name}.json"
    
    def start_recording(self):
        """Start recording a new test case."""
        if self.proxy:
            self.proxy.clear()
        
    def stop_recording(self, test_name: str):
        """Stop recording and save or verify events."""
        if MODE == TestMode.PASS_THROUGH:
            return
            
        recording_path = self.get_recording_path(test_name)
        
        if MODE == TestMode.RECORD:
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

def test_algorithmic_manipulation(test_session):
    """Test basic algorithmic manipulation (Tutorial 2)."""
    def test_case():
        Clock.bpm = 240
        
        # Basic pattern with manipulation
        p1 = Player()
        Clock.set_time(0)
        p1 >> charm([0,1,2,3]) + [0,0,0,2]
        time.sleep(3)
        
        # Pattern with groups
        p1 >> charm([0,1,2,3]) + [0,1,[0,(0,2)]]
        time.sleep(3)
        
        Clock.clear()
        
    run_test_case('test_algorithmic_manipulation', test_session, test_case)

def test_playing_samples(test_session):
    """Test sample playback features (Tutorial 3)."""
    def test_case():
        Clock.bpm = 240
        
        # Basic sample playback
        d1 = Player()
        d1 >> play("x-o[-o]")
        Clock.set_time(0)
        time.sleep(3)
        
        # Complex pattern with brackets
        d1 >> play("x[--]o(=[-o])")
        Clock.set_time(0)
        time.sleep(4)
        
        # Simultaneous patterns
        d1 >> play("<X...><-...>")
        Clock.set_time(0)
        time.sleep(2)
        
        # Random patterns (with only one sample for consistent result)
        d1 >> play("{oooo}")
        Clock.set_time(0)
        time.sleep(2)
        
        Clock.clear()
        
    run_test_case('test_playing_samples', test_session, test_case)

def test_pattern_operations(test_session):
    """Test pattern operations (Tutorial 4)."""
    def test_case():
        Clock.bpm = 240
        
        # Basic pattern playing
        p1 = Player()
        p1 >> pluck(P[0,1,2,P(4,6,8),7,8])
        Clock.set_time(0)
        time.sleep(3)
        
        # Pattern with duration spread
        p1 >> pluck(P*(0,2,4), dur=1/2)
        Clock.set_time(0)
        time.sleep(3)
        
        # Pattern with sustain spread
        p1 >> pluck(P+(0,2,4), dur=2, sus=3)
        Clock.set_time(0)
        time.sleep(3)
        
        Clock.clear()
        
    run_test_case('test_pattern_operations', test_session, test_case)

def test_player_attributes(test_session):
    """Test player attributes and following (Tutorial 5)."""
    def test_case():
        Clock.bpm = 240
        
        # Basic pitch following
        p1 = Player()
        p2 = Player()
        p1 >> pluck([0,1,2,3])
        Clock.set_time(0)
        p2 >> star().follow(p1) + 2
        time.sleep(3)
        
        # Conditional amplitudes
        p1 >> pluck([0,1,2,3], amp=(p1.degree==1)*4)
        Clock.set_time(0)
        time.sleep(3)
        
        Clock.clear()
        
    run_test_case('test_player_attributes', test_session, test_case)

def test_time_vars(test_session):
    """Test TimeVar functionality (Tutorial 10)."""
    def test_case():
        Clock.bpm = 240
        Clock.set_time(0)
        
        # Basic TimeVar
        a = var([0,3], 2)  # Shorter duration due to faster BPM
        b1 = Player()
        b1 >> bass(a, dur=PDur(3,8))
        Clock.set_time(0)
        time.sleep(3)
        
        # Pattern TimeVar
        pattern1 = P[0, 1, 2, 3]
        pattern2 = P[4, 5, 6, 7]
        p1 = Player()
        p1 >> pluck(Pvar([pattern1, pattern2], 2), dur=1/4)
        Clock.set_time(0)
        time.sleep(3)
        
        Clock.clear()
        
    run_test_case('test_time_vars', test_session, test_case)

def test_clock_operations(test_session):
    """Test clock operations (Tutorial 7)."""
    def test_case():
        # Set faster BPM
        Clock.bpm = 240
        Clock.set_time(0)
        
        # Basic pattern to test timing
        d1 = Player()
        d1 >> play("x-o-")
        Clock.set_time(0)
        time.sleep(3)
        
        # Change BPM mid-sequence
        Clock.bpm = 180
        time.sleep(3)
        
        Clock.clear()
        
    run_test_case('test_clock_operations', test_session, test_case)

if __name__ == "__main__":
    print("""
Usage modes:
    Record mode:
        RENARDO_TEST_MODE=record pytest test_functional_renardo_sc.py -v

    Verify mode (default):
        RENARDO_TEST_MODE=verify pytest test_functional_renardo_sc.py -v
        # or simply:
        pytest test_functional_renardo_sc.py -v

    Pass-through mode (direct to SC):
        RENARDO_TEST_MODE=pass_through pytest test_functional_renardo_sc.py -v
    """)