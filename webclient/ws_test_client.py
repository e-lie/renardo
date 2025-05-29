#!/usr/bin/env python3
import json
import time
import sys
import asyncio
import websockets


async def ws_test_client():
    uri = "ws://localhost:12345/ws"  # Adjust port if different
    connection_attempts = 0
    max_attempts = 5
    reconnect_delay = 5  # seconds

    print(f"WebSocket Test Client - Connecting to {uri}")

    while connection_attempts < max_attempts:
        try:
            connection_attempts += 1
            print(f"Connection attempt {connection_attempts}...")

            async with websockets.connect(uri) as websocket:
                print(f"Connection established to {uri}")

                # Keep track of connection stability
                connected_time = time.time()
                message_count = 0

                # Send an initial message
                init_message = json.dumps(
                    {
                        "type": "ping",
                        "data": {
                            "client": "python_test_client",
                            "timestamp": time.time(),
                        },
                    }
                )
                await websocket.send(init_message)
                print(f"Sent initial ping message")

                # Set up ping interval
                ping_interval = 5  # seconds
                last_ping_time = time.time()

                # Listen for messages in a loop
                while True:
                    # Set up a timeout for receiving messages
                    try:
                        # Send periodic pings to keep connection alive
                        if time.time() - last_ping_time > ping_interval:
                            ping_message = json.dumps(
                                {
                                    "type": "ping",
                                    "data": {
                                        "client": "python_test_client",
                                        "timestamp": time.time(),
                                    },
                                }
                            )
                            await websocket.send(ping_message)
                            last_ping_time = time.time()
                            print(f"Sent ping message")

                        # Try to receive with a timeout
                        response = await asyncio.wait_for(websocket.recv(), timeout=10)
                        message_count += 1

                        # Parse and display the response
                        try:
                            parsed = json.loads(response)
                            print(
                                f"Received message #{message_count}: {parsed.get('type', 'unknown')}"
                            )

                            # Optionally print full message if short
                            if len(response) < 200:
                                print(f"  Content: {response}")
                            else:
                                print(f"  Content length: {len(response)} bytes")

                            # Test code execution if wanted
                            if message_count % 10 == 0:
                                print("Sending test code execution...")
                                code_message = json.dumps(
                                    {
                                        "type": "execute_code",
                                        "data": {
                                            "code": "# Test code\nd1 >> play('x-o-')"
                                        },
                                    }
                                )
                                await websocket.send(code_message)
                        except json.JSONDecodeError:
                            print(f"Received non-JSON message: {response[:100]}...")

                    except asyncio.TimeoutError:
                        duration = time.time() - connected_time
                        print(
                            f"No message received in 10 seconds. Connection duration: {duration:.1f}s, Message count: {message_count}"
                        )
                        # Continue the loop, don't disconnect

                    except websockets.exceptions.ConnectionClosed as e:
                        duration = time.time() - connected_time
                        print(
                            f"Connection closed: {e}. Connection duration: {duration:.1f}s, Message count: {message_count}"
                        )
                        break

        except (ConnectionRefusedError, websockets.exceptions.WebSocketException) as e:
            print(f"Connection error: {e}")
            if connection_attempts < max_attempts:
                print(f"Retrying in {reconnect_delay} seconds...")
                await asyncio.sleep(reconnect_delay)
            else:
                print("Maximum connection attempts reached. Exiting.")
                break

        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected. Exiting gracefully.")
            break

        except Exception as e:
            print(f"Unexpected error: {e}")
            break


if __name__ == "__main__":
    try:
        asyncio.run(ws_test_client())
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Exiting.")
        sys.exit(0)
