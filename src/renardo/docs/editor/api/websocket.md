# WebSocket API

The Renardo WebSocket API provides real-time communication between the client and the server. This page documents the available message types and their formats.

## Connection

The WebSocket endpoint is available at:

```
ws://<server-address>/ws
```

Where `<server-address>` is the host and port where Renardo is running (typically `localhost:7998`).

## Message Format

All messages use a JSON format with the following structure:

```json
{
  "type": "message_type",
  "data": {
    // Message-specific data
  }
}
```

## Client to Server Messages

### Execute Code

Executes Python code in the Renardo environment.

```json
{
  "type": "execute_code",
  "data": {
    "code": "p1 >> pluck([0, 1, 2, 3])",
    "requestId": 1234567890
  }
}
```

- `code` (string): The Python code to execute
- `requestId` (number): A unique identifier for this execution request

### Stop All

Stops all running patterns (equivalent to `Clock.clear()`).

```json
{
  "type": "stop_all",
  "data": {}
}
```

### Get State

Requests the current state of the Renardo environment.

```json
{
  "type": "get_state",
  "data": {}
}
```

## Server to Client Messages

### Code Execution Result

Response to a code execution request.

```json
{
  "type": "code_execution_result",
  "data": {
    "requestId": 1234567890,
    "success": true,
    "output": "Output text",
    "error": null
  }
}
```

- `requestId` (number): The ID of the original execution request
- `success` (boolean): Whether the execution succeeded
- `output` (string): Output from the execution (if any)
- `error` (string): Error message (if execution failed)

### Console Message

Updates to the console output.

```json
{
  "type": "console_message",
  "data": {
    "timestamp": "12:34:56",
    "level": "info",
    "message": "Console message text"
  }
}
```

- `timestamp` (string): Time the message was generated
- `level` (string): Message level ("info", "warn", "error", "success")
- `message` (string): The message content

### State Update

Updates to the Renardo state.

```json
{
  "type": "state_update",
  "data": {
    "clock": {
      "bpm": 120,
      "playing": true
    },
    "players": [
      {
        "name": "p1",
        "active": true,
        "attributes": {
          "dur": 1,
          "amp": 0.5
        }
      }
    ]
  }
}
```

## Error Handling

If an error occurs during processing, the server may send an error message:

```json
{
  "type": "error",
  "data": {
    "message": "Error message",
    "code": "error_code"
  }
}
```

## Event Handling

To handle these messages in JavaScript:

```javascript
const socket = new WebSocket('ws://localhost:7998/ws');

socket.onopen = () => {
  console.log('Connected to Renardo WebSocket');
};

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'code_execution_result':
      handleExecutionResult(message.data);
      break;
    case 'console_message':
      updateConsole(message.data);
      break;
    case 'state_update':
      updateState(message.data);
      break;
    case 'error':
      handleError(message.data);
      break;
  }
};

socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};

socket.onclose = () => {
  console.log('Disconnected from Renardo WebSocket');
};

// Function to send code for execution
function executeCode(code) {
  const requestId = Date.now();
  socket.send(JSON.stringify({
    type: 'execute_code',
    data: {
      code: code,
      requestId: requestId
    }
  }));
  return requestId;
}
```

## Connection Status

The WebSocket connection will automatically reconnect if disconnected. The client can check the connection status by sending a ping message and waiting for a pong response.

```json
{
  "type": "ping",
  "data": {}
}
```

Response:

```json
{
  "type": "pong",
  "data": {
    "timestamp": 1626912345678
  }
}
```