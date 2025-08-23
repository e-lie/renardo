--[[
MIDI Note Server for Renardo/Reaside
=====================================

Dedicated high-performance MIDI message handler for low-latency note triggering.
Polls ExtState queue for MIDI messages and sends them to tracks via StuffMIDIMessage.

This script runs independently from reaside_server.lua for better performance.
]]

-- Configuration
local DEBUG = false  -- Set to true to enable debug logging
local POLL_RATE = 100  -- Hz - how often to check for messages

-- Debug logging function
function log(msg)
  if DEBUG then
    reaper.ShowConsoleMsg("[midi_note_server] " .. tostring(msg) .. "\n")
  end
end

-- Simple JSON parser (handles basic cases)
function parse_json(str)
  if not str or str == "" then
    return nil
  end
  
  -- Remove whitespace
  str = str:gsub("^%s*", ""):gsub("%s*$", "")
  
  -- Try to parse as a Lua table using load (Lua 5.2+) or loadstring (Lua 5.1)
  local loadfn = load or loadstring
  local func, err = loadfn("return " .. str)
  if func then
    local success, result = pcall(func)
    if success then
      return result
    end
  end
  
  -- Simplified JSON to Lua conversion
  -- Replace JSON arrays with Lua tables
  local lua_str = str:gsub('%[', '{'):gsub('%]', '}')
  
  -- Replace JSON object syntax with Lua table syntax
  -- This handles "key": value patterns
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*"([^"]*)"', '["%1"] = "%2"')  -- "key": "string value"
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*([%d%.%-]+)', '["%1"] = %2')   -- "key": number
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*true', '["%1"] = true')        -- "key": true
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*false', '["%1"] = false')      -- "key": false
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*null', '["%1"] = nil')         -- "key": null
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*{', '["%1"] = {')              -- "key": { nested object
  
  -- Try parsing the converted string
  func, err = loadfn("return " .. lua_str)
  if func then
    local success, result = pcall(func)
    if success then
      return result
    end
  end
  
  log("Failed to parse JSON: " .. tostring(err))
  return nil
end

-- Message queue handler for ExtState polling
function handle_message_queue()
  -- Check for messages in ExtState queue
  local raw_message = reaper.GetExtState("reaside_queue", "message")
  
  if raw_message and raw_message ~= "" then
    -- Clear the message immediately to avoid processing it twice
    reaper.DeleteExtState("reaside_queue", "message", false)
    
    -- Parse the message
    local message = parse_json(raw_message)
    
    if message and type(message) == "table" then
      -- Route to appropriate handler based on action
      if message.action then
        handle_queue_action(message.action, message.args or {})
      end
    end
  end
end

-- Handle specific actions from the message queue
function handle_queue_action(action, args)
  log("Queue action: " .. action .. " with " .. #args .. " args")
  
  -- MIDI Note On
  if action == "midi_note_on" then
    -- Expected args: [track_index, channel, note, velocity]
    if #args >= 4 then
      local track_idx = tonumber(args[1])
      local channel = tonumber(args[2]) - 1  -- Convert to 0-based
      local note = tonumber(args[3])
      local velocity = tonumber(args[4])
      
      if track_idx and channel and note and velocity then
        send_midi_to_track(track_idx, 0x90 + channel, note, velocity)  -- 0x90 = Note On
        log(string.format("MIDI Note On: track=%d, ch=%d, note=%d, vel=%d", 
                         track_idx, channel+1, note, velocity))
      else
        log("Invalid MIDI note_on parameters")
      end
    else
      log("midi_note_on requires 4 args: track_index, channel, note, velocity")
    end
  
  -- MIDI Note Off
  elseif action == "midi_note_off" then
    -- Expected args: [track_index, channel, note, velocity]
    if #args >= 3 then
      local track_idx = tonumber(args[1])
      local channel = tonumber(args[2]) - 1  -- Convert to 0-based
      local note = tonumber(args[3])
      local velocity = tonumber(args[4]) or 0  -- Default velocity 0 for note off
      
      if track_idx and channel and note then
        send_midi_to_track(track_idx, 0x80 + channel, note, velocity)  -- 0x80 = Note Off
        log(string.format("MIDI Note Off: track=%d, ch=%d, note=%d, vel=%d", 
                         track_idx, channel+1, note, velocity))
      else
        log("Invalid MIDI note_off parameters")
      end
    else
      log("midi_note_off requires at least 3 args: track_index, channel, note, [velocity]")
    end
  
  else
    log("Unknown queue action: " .. action)
  end
end

-- Send MIDI message to a specific track's virtual MIDI keyboard
function send_midi_to_track(track_index, status, data1, data2)
  -- Get the track (0-based index)
  local track = reaper.GetTrack(0, track_index)
  if not track then
    log("Track not found at index: " .. track_index)
    return
  end
  
  -- Make sure the track is selected and armed for recording
  -- This ensures the MIDI message goes to the right place
  reaper.SetTrackSelected(track, true)
  
  -- Check if track is record armed for MIDI input
  local rec_input = reaper.GetMediaTrackInfo_Value(track, "I_RECINPUT")
  if rec_input < 4096 then  -- Not set to MIDI input
    -- Set to All MIDI inputs, all channels
    reaper.SetMediaTrackInfo_Value(track, "I_RECINPUT", 4096)
  end
  
  -- Ensure track is record armed
  local rec_arm = reaper.GetMediaTrackInfo_Value(track, "I_RECARM")
  if rec_arm == 0 then
    reaper.SetMediaTrackInfo_Value(track, "I_RECARM", 1)
  end
  
  -- Enable track record monitoring
  local rec_mon = reaper.GetMediaTrackInfo_Value(track, "I_RECMON")
  if rec_mon == 0 then
    reaper.SetMediaTrackInfo_Value(track, "I_RECMON", 1)  -- Set to monitor input
  end
  
  -- StuffMIDIMessage(mode, msg1, msg2, msg3)
  -- mode: 0 = to virtual MIDI keyboard
  reaper.StuffMIDIMessage(0, status, data1, data2)
  
  log(string.format("Sent MIDI to track %d: status=%02X, data1=%d, data2=%d", 
                    track_index, status, data1, data2))
end

-- Main loop function
function main_loop()
  -- Poll for messages
  handle_message_queue()
  
  -- Continue running at specified rate
  reaper.defer(main_loop)
end

-- Initialize
function init()
  reaper.ShowConsoleMsg("MIDI Note Server started\n")
  log("MIDI Note Server initialized - polling at " .. POLL_RATE .. " Hz")
  
  -- Store status in ExtState
  reaper.SetExtState("midi_note_server", "status", "running", false)
  reaper.SetExtState("midi_note_server", "poll_rate", tostring(POLL_RATE), false)
  
  -- Start main loop
  main_loop()
end

-- Cleanup on exit
function onexit()
  reaper.DeleteExtState("midi_note_server", "status", false)
  reaper.DeleteExtState("midi_note_server", "poll_rate", false)
  reaper.ShowConsoleMsg("MIDI Note Server stopped\n")
end

-- Set exit handler
reaper.atexit(onexit)

-- Start the server
init()