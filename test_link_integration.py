#!/usr/bin/env python3
"""
Test script for Ableton Link integration in TempoClock
"""

import sys
import time

# Add renardo_lib to path
sys.path.insert(0, '/Users/jxfer/Desktop/renardo_perf_stable_reaper/renardo_lib')

from renardo_lib.TempoClock import TempoClock

def test_link_integration():
    """Test basic Link integration"""

    print("=" * 50)
    print("Testing Ableton Link Integration")
    print("=" * 50)

    # Create TempoClock instance
    clock = TempoClock(bpm=120)
    clock.debugging = True

    # Start the clock
    clock.start()
    time.sleep(1)

    print("\n1. Testing Link sync activation...")
    result = clock.sync_to_link(enabled=True, sync_interval=1)

    if result:
        print("✓ Link sync enabled successfully")
    else:
        print("✗ Link sync failed to enable")
        return False

    # Wait a bit for Link to initialize
    time.sleep(2)

    print("\n2. Checking Link status...")
    clock.link_status()

    print("\n3. Testing tempo change from TempoClock...")
    print("Setting BPM to 140...")
    clock.bpm = 140
    time.sleep(2)
    clock.link_status()

    print("\n4. Monitoring Link for 10 seconds...")
    print("(Try changing tempo in Ableton Live or another Link app)")

    for i in range(10):
        session = clock.link.captureSessionState()
        link_time = clock.link.clock().micros()

        tempo = session.tempo()
        beat = session.beatAtTime(link_time, 4)
        phase = session.phaseAtTime(link_time, 4)
        num_peers = clock.link.numPeers()

        # Visual phase indicator
        phase_display = "█" * int(phase) + "░" * (4 - int(phase))

        print(f"[{i+1:2d}/10] BPM: {tempo:6.2f} | Beat: {beat:6.2f} | {phase_display} | Peers: {num_peers}")
        time.sleep(1)

    print("\n5. Disabling Link...")
    clock.disable_link()
    print("✓ Link disabled")

    print("\n" + "=" * 50)
    print("Test completed successfully!")
    print("=" * 50)

    return True

def test_link_availability():
    """Test if LinkPython is available"""
    try:
        import link
        print("✓ LinkPython is installed")
        return True
    except ImportError:
        print("✗ LinkPython is NOT installed")
        print("Install with: pip install LinkPython-extern")
        return False

if __name__ == "__main__":
    print("\nChecking LinkPython availability...")
    if not test_link_availability():
        print("\nPlease install LinkPython-extern first:")
        print("  pip install LinkPython-extern")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Starting integration test...")
    print("=" * 50)

    try:
        success = test_link_integration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
