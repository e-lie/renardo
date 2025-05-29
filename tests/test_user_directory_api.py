#!/usr/bin/env python3
"""
Test script for user directory API endpoints
"""

import json
import time
import requests
from pathlib import Path


def wait_for_server(url, timeout=10):
    """Wait for the server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.5)
    return False


def test_user_directory_api():
    base_url = "http://localhost:12345"

    # Check if server is running
    if not wait_for_server(f"{base_url}/api/state"):
        print("Server is not running. Please start the Renardo server first.")
        return

    print("Testing user directory API endpoints...")

    # 1. Test GET user directory
    print("\n1. Testing GET /api/settings/user-directory")
    response = requests.get(f"{base_url}/api/settings/user-directory")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    if data.get("success"):
        current_path = data.get("path")
        print(f"Current user directory: {current_path}")

    # 2. Test POST open user directory
    print("\n2. Testing POST /api/settings/user-directory/open")
    response = requests.post(f"{base_url}/api/settings/user-directory/open")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    # 3. Test POST move user directory (without actually moving for safety)
    print("\n3. Testing POST /api/settings/user-directory/move validation")

    # Test with missing path
    response = requests.post(f"{base_url}/api/settings/user-directory/move", json={})
    print(f"Status (missing path): {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    # Test with relative path (should fail)
    response = requests.post(
        f"{base_url}/api/settings/user-directory/move", json={"path": "relative/path"}
    )
    print(f"\nStatus (relative path): {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    print("\nAll API tests completed!")


if __name__ == "__main__":
    test_user_directory_api()
