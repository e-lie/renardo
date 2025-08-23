--[[
MIDI Note Server for Renardo/Reaside
=====================================

Dedicated high-performance MIDI message handler for low-latency note triggering.
Polls ExtState queue for MIDI messages and sends them to tracks via StuffMIDIMessage.

This script runs independently from reaside_server.lua for better performance.
]]

-- Configuration
local DEBUG = true  -- Set to true to enable debug logging
local POLL_RATE = 200  -- Hz - how often to check for messages (increased for better timing accuracy)

-- Timing state
local clock_info = {
  tempo_clock_time = 0,  -- Current TempoClock time in beats
  system_time = 0,       -- System time when clock was updated
  bpm = 120              -- Current BPM
}

-- Message queue for timed events
local timed_messages = {}

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
  -- This handles "key": value patterns - order matters!
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*{', '["%1"] = {')              -- "key": { nested object (do this first)
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*"([^"]*)"', '["%1"] = "%2"')  -- "key": "string value"
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*([%d%.%-]+)', '["%1"] = %2')   -- "key": number
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*true', '["%1"] = true')        -- "key": true
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*false', '["%1"] = false')      -- "key": false
  lua_str = lua_str:gsub('"([^"]+)"%s*:%s*null', '["%1"] = nil')         -- "key": null
  
  -- Try parsing the converted string
  func, err = loadfn("return " .. lua_str)
  if func then
    local success, result = pcall(func)
    if success then
      return result
    end
  end
  
  log("Failed to parse JSON: " .. tostring(err))
  if string.len(str) < 200 then
    log("Original: " .. str)
    log("Converted: " .. lua_str)
  end
  return nil
end

-- Get current TempoClock time estimate
function get_tempo_clock_time()
  -- Use a local timer that starts from 0
  local current_time = reaper.time_precise()
  
  -- If we haven't synced yet, just return 0
  if clock_info.system_time == 0 then
    return 0
  end
  
  -- Calculate elapsed time since last clock update
  local elapsed = current_time - clock_info.system_time
  
  -- Convert elapsed seconds to beats
  local elapsed_beats = (elapsed * clock_info.bpm) / 60.0
  
  -- Return estimated current clock time
  return clock_info.tempo_clock_time + elapsed_beats
end

-- Update clock sync from ExtState
function update_clock_sync()
  -- Check for clock sync update
  local clock_data = reaper.GetExtState("midi_clock_sync", "current")
  if clock_data and clock_data ~= "" then
    local sync = parse_json(clock_data)
    if sync then
      clock_info.tempo_clock_time = sync.clock_time or clock_info.tempo_clock_time
      -- Store Reaper's time when we received this sync
      clock_info.system_time = reaper.time_precise()
      clock_info.bpm = sync.bpm or clock_info.bpm
      -- Removed clock sync logging to reduce console spam
    end
  end
end

-- Process timed messages that are ready
function process_timed_messages()
  local current_clock = get_tempo_clock_time()
  local messages_to_remove = {}
  
  -- Log queue status periodically
  if #timed_messages > 0 and math.floor(current_clock * 10) % 10 == 0 then
    log(string.format("Queue: %d messages, current_clock=%.3f, next_msg_time=%.3f", 
                     #timed_messages, current_clock, 
                     timed_messages[1] and timed_messages[1].time or -1))
  end
  
  -- Check each timed message
  for i, msg in ipairs(timed_messages) do
    if msg.time <= current_clock then
      -- Execute the message
      log(string.format("Executing timed message: action=%s at clock=%.3f (scheduled=%.3f)", 
                       msg.action, current_clock, msg.time))
      handle_queue_action(msg.action, msg.args or {})
      table.insert(messages_to_remove, i)
    end
  end
  
  -- Remove processed messages (in reverse order to maintain indices)
  for i = #messages_to_remove, 1, -1 do
    table.remove(timed_messages, messages_to_remove[i])
  end
end

-- Message queue handler for ExtState polling
function handle_message_queue()
  -- Check for batch messages in ExtState queue
  local raw_batch = reaper.GetExtState("midi_batch", "messages")
  
  if raw_batch and raw_batch ~= "" then
    log("Found batch in ExtState, length: " .. string.len(raw_batch))
    -- Clear the batch immediately
    reaper.DeleteExtState("midi_batch", "messages", false)
    
    -- Parse the batch
    local batch = parse_json(raw_batch)
    
    if batch and type(batch) == "table" then
      -- Check if it's a batch or single message
      if batch.messages then
        log("Processing batch with " .. #batch.messages .. " messages")
        -- It's a batch with multiple timed messages
        for i, msg in ipairs(batch.messages) do
          if msg.time then
            -- Add to timed queue
            table.insert(timed_messages, msg)
            log(string.format("  Message %d: %s at time %.3f", i, msg.action, msg.time))
          else
            -- Execute immediately
            log(string.format("  Message %d: %s (immediate)", i, msg.action))
            handle_queue_action(msg.action, msg.args or {})
          end
        end
        -- Sort by time
        table.sort(timed_messages, function(a, b) return a.time < b.time end)
        log("Added " .. #batch.messages .. " messages to queue, total queued: " .. #timed_messages)
      elseif batch.action then
        -- Single message for immediate execution
        log("Single message: " .. batch.action)
        handle_queue_action(batch.action, batch.args or {})
      end
    else
      log("Failed to parse batch")
    end
  end
  
  -- Also check old single message queue for compatibility
  local raw_message = reaper.GetExtState("reaside_queue", "message")
  if raw_message and raw_message ~= "" then
    reaper.DeleteExtState("reaside_queue", "message", false)
    local message = parse_json(raw_message)
    if message and type(message) == "table" and message.action then
      handle_queue_action(message.action, message.args or {})
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
  -- Update clock sync
  update_clock_sync()
  
  -- Process any timed messages that are ready
  process_timed_messages()
  
  -- Poll for new messages
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