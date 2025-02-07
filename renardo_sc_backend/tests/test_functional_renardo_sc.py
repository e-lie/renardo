import pytest
from pathlib import Path
import json
import time
from datetime import datetime
import os
import shutil
from renardo_sc_backend.osc_proxy import OSCProxy
from renardo_lib.runtime import Player, blip, Clock

# Configuration
RECORD_MODE = os.environ.get('RENARDO_TEST_RECORD', 'False').lower() == 'true'
TEST_DATA_DIR = Path('osc_test_recording')
TIMING_TOLERANCE = 0.1

class TestSession:
    """Manages test recording sessions."""
    
    def __init__(self):
        self.session_dir = None
        if RECORD_MODE:
            # Create new session directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_dir = TEST_DATA_DIR / f"session_{timestamp}"
            self.session_dir.mkdir(parents=True, exist_ok=True)
        else:
            # Find most recent session
            if TEST_DATA_DIR.exists():
                sessions = sorted(TEST_DATA_DIR.glob("session_*"))
                if sessions:
                    self.session_dir = sessions[-1]
    
    def get_recording_path(self, test_name: str) -> Path:
        """Get path for recording or comparing a test."""
        if not self.session_dir:
            raise RuntimeError("No session directory available")
        return self.session_dir / f"{test_name}.json"

@pytest.fixture(scope="session")
def test_session():
    """Fixture providing test session management."""
    return TestSession()

@pytest.fixture
def osc_proxy():
    """Fixture that provides a configured OSC proxy for testing."""
    proxy = OSCProxy(listen_port=57120, forward_port=57110)
    proxy.start()
    yield proxy
    proxy.stop()

def compare_events(actual_events, expected_events, timing_tolerance=TIMING_TOLERANCE):
    """Compare two sequences of OSC events."""
    assert len(actual_events) == len(expected_events), \
        f"Incorrect number of events. Expected: {len(expected_events)}, Got: {len(actual_events)}"

    for actual, expected in zip(actual_events, expected_events):
        # Check OSC address
        assert actual.address == expected["address"], \
            f"Incorrect OSC address. Expected: {expected['address']}, Got: {actual.address}"

        # Check arguments
        assert actual.args == expected["args"], \
            f"Incorrect arguments. Expected: {expected['args']}, Got: {actual.args}"

        # Check timing (with tolerance)
        assert abs(actual.timestamp - expected["timestamp"]) <= timing_tolerance, \
            f"Incorrect timing. Expected: {expected['timestamp']}, Got: {actual.timestamp}"

def run_test_case(test_name: str, osc_proxy, test_session, test_func):
    """Run a test case in either record or verify mode."""
    recording_path = test_session.get_recording_path(test_name)
    
    # Run the test function
    test_func()
    
    if RECORD_MODE:
        # Save recorded events
        with open(recording_path, 'w') as f:
            events_dict = [asdict(event) for event in osc_proxy.events]
            json.dump(events_dict, f, indent=2)
        print(f"Recorded test case '{test_name}' to {recording_path}")
    else:
        # Compare with recorded events
        with open(recording_path) as f:
            expected_events = json.load(f)
        compare_events(osc_proxy.events, expected_events)

    # Clear events for next test
    osc_proxy.clear()

def test_blip_1(osc_proxy, test_session):
    """Test basic blip pattern."""
    def test_case():
        time.sleep(3)  # Wait for system to stabilize
        b1 = Player()
        b1 >> blip([0,2,4,5,6])
        Clock.set_time(0)
        time.sleep(3)  # Wait for events to be generated
        Clock.clear()
    
    run_test_case('test_blip_1', osc_proxy, test_session, test_case)

def test_blip_2(osc_proxy, test_session):
    """Test another blip pattern."""
    def test_case():
        time.sleep(3)
        b1 = Player()
        b1 >> blip([0,1,2,3])
        Clock.set_time(0)
        time.sleep(3)
        Clock.clear()
    
    run_test_case('test_blip_2', osc_proxy, test_session, test_case)

if __name__ == "__main__":
    # Instructions for running tests
    print("""
Run tests in record mode:
    RENARDO_TEST_RECORD=true pytest test_functional_renardo_sc.py -v

Run tests in verify mode:
    pytest test_functional_renardo_sc.py -v
    """)