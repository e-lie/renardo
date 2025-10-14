#!/usr/bin/env python3
"""
Test script for subprocess logging with separate log files.
"""

import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from renardo.process_manager.base import ManagedProcess


class TestProcess(ManagedProcess):
    """Simple test process that runs 'echo' commands."""

    def _build_command(self) -> list:
        """Build a simple test command that outputs some text."""
        return ["bash", "-c", "echo 'Line 1: stdout message'; sleep 1; echo 'Line 2: another message'; sleep 1; echo 'Line 3: final message'"]


def main():
    print("Testing subprocess logging with separate log files...\n")

    # Create test process without timestamps (default)
    print("1. Creating test process without timestamps...")
    process1 = TestProcess(process_id="test1", process_type="test")

    print(f"   Expected log file: /tmp/renardo-test-test1.log")

    # Start the process
    if process1.start():
        print("   Process started successfully!")
        print("   Waiting for process to complete...")

        # Wait for process to finish
        time.sleep(5)

        # Stop the process
        process1.stop()
        print("   Process stopped.\n")
    else:
        print("   Failed to start process!\n")
        return 1

    # Create another test process with timestamps
    print("2. Creating test process WITH timestamps...")
    process2 = TestProcess(
        process_id="test2",
        process_type="test",
        config={"log_with_timestamp": True}
    )

    print(f"   Expected log file: /tmp/renardo-test-test2.log")

    # Start the process
    if process2.start():
        print("   Process started successfully!")
        print("   Waiting for process to complete...")

        # Wait for process to finish
        time.sleep(5)

        # Stop the process
        process2.stop()
        print("   Process stopped.\n")
    else:
        print("   Failed to start process!\n")
        return 1

    # Check if log files were created
    print("3. Checking log files...")
    log1 = Path("/tmp/renardo-test-test1.log")
    log2 = Path("/tmp/renardo-test-test2.log")

    if log1.exists():
        print(f"   ✓ Log file 1 exists: {log1}")
        print(f"   Content (without timestamps):")
        with open(log1) as f:
            for line in f:
                print(f"     {line.rstrip()}")
    else:
        print(f"   ✗ Log file 1 NOT found: {log1}")

    print()

    if log2.exists():
        print(f"   ✓ Log file 2 exists: {log2}")
        print(f"   Content (with timestamps):")
        with open(log2) as f:
            for line in f:
                print(f"     {line.rstrip()}")
    else:
        print(f"   ✗ Log file 2 NOT found: {log2}")

    print("\nTest completed!")
    print("\nYou can also check the logs manually:")
    print(f"  cat {log1}")
    print(f"  cat {log2}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
