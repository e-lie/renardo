--[[
reaside HTTP API Bridge

This script provides a bridge between REAPER's HTTP API and the ReaScript API.

Features:
- Doesn't require Python to be enabled in REAPER
- Works with basic Lua capabilities built into REAPER
- Provides access to all ReaScript API functions
- Runs continuously in the background to process API calls

Installation:
1. In REAPER, go to Actions > Show Action List
2. Click "New Action..." > "Load ReaScript..."
3. Select this file
4. Run the script once to initialize and start the API bridge
]]

-- Configuration
local DEBUG = true  -- Set to true to enable debug logging
local SECTION = "reaside"
local REAPER_VERSION = reaper.GetAppVersion()

-- OSC Configuration
local OSC_ENABLED = true  -- Set to false to disable OSC functionality
local OSC_SEND_PORT = 8001  -- Port to send OSC messages to Python client
local OSC_RECEIVE_PORT = 8000  -- Port to receive OSC messages from Python client
local OSC_HOST = "127.0.0.1"  -- Host for OSC communication

-- Pointer cache to store userdata objects (MediaTrack, MediaItem, etc.)
local pointer_cache = {}
local pointer_counter = 0

-- Debug logging function
function log(msg)
  if DEBUG then
    reaper.ShowConsoleMsg("[reaside] " .. tostring(msg) .. "\n")
  end
end

-- OSC state tracking
local osc_device_id = nil
local last_transport_state = -1
local last_time_position = -1
local last_beat_position = -1

-- Initialize OSC device
function init_osc()
  if not OSC_ENABLED then
    return false
  end
  
  -- Try to find existing OSC device or create one
  for i = 0, reaper.GetNumMIDIOutputs() - 1 do
    local retval, name = reaper.GetMIDIOutputName(i, "")
    if name and name:find("OSC") then
      osc_device_id = i
      log("Found existing OSC device: " .. name)
      break
    end
  end
  
  -- If no OSC device found, we'll use the local message system
  log("OSC functionality initialized (using local messaging)")
  return true
end

-- Send OSC message to Python client
function send_osc_message(address, ...)
  if not OSC_ENABLED then
    return
  end
  
  local args = {...}
  local msg = address
  
  -- Format arguments
  for i, arg in ipairs(args) do
    msg = msg .. " " .. tostring(arg)
  end
  
  -- Use REAPER's OSC sending capability
  if reaper.OscLocalMessageToHost then
    reaper.OscLocalMessageToHost(msg, OSC_SEND_PORT)
    log("Sent OSC: " .. msg)
  else
    -- Fallback: store in ExtState for Python to poll
    set_ext_state("reaside_osc", "message", {
      address = address,
      args = args,
      timestamp = os.time()
    }, false)
  end
end

-- Handle incoming OSC messages
function handle_osc_message(address, args)
  log("Received OSC: " .. address .. " with " .. #args .. " args")
  
  -- Transport control
  if address == "/transport/play" then
    reaper.Main_OnCommand(40007, 0)  -- Transport: Play/stop
    
  elseif address == "/transport/pause" then
    reaper.Main_OnCommand(40001, 0)  -- Transport: Play/pause
    
  elseif address == "/transport/stop" then
    reaper.Main_OnCommand(40016, 0)  -- Transport: Stop
    
  elseif address == "/transport/record" then
    reaper.Main_OnCommand(40044, 0)  -- Transport: Record
    
  -- Time positioning
  elseif address == "/time/goto" and #args >= 1 then
    local time_seconds = tonumber(args[1])
    if time_seconds then
      reaper.SetEditCurPos(time_seconds, true, true)
    end
    
  elseif address == "/beat/goto" and #args >= 1 then
    local beat = tonumber(args[1])
    if beat then
      local time_seconds = reaper.TimeMap2_beatsToTime(0, beat)
      reaper.SetEditCurPos(time_seconds, true, true)
    end
    
  -- Track operations
  elseif address:match("^/track/(%d+)/volume$") and #args >= 1 then
    local track_id = tonumber(address:match("^/track/(%d+)/volume$"))
    local volume = tonumber(args[1])
    if track_id and volume then
      local track = reaper.GetTrack(0, track_id - 1)  -- Convert to 0-based
      if track then
        reaper.SetMediaTrackInfo_Value(track, "D_VOL", volume)
      end
    end
    
  elseif address:match("^/track/(%d+)/pan$") and #args >= 1 then
    local track_id = tonumber(address:match("^/track/(%d+)/pan$"))
    local pan = tonumber(args[1])
    if track_id and pan then
      local track = reaper.GetTrack(0, track_id - 1)  -- Convert to 0-based
      if track then
        reaper.SetMediaTrackInfo_Value(track, "D_PAN", pan)
      end
    end
    
  elseif address:match("^/track/(%d+)/mute$") and #args >= 1 then
    local track_id = tonumber(address:match("^/track/(%d+)/mute$"))
    local mute = tonumber(args[1])
    if track_id and mute ~= nil then
      local track = reaper.GetTrack(0, track_id - 1)  -- Convert to 0-based
      if track then
        reaper.SetMediaTrackInfo_Value(track, "B_MUTE", mute)
      end
    end
    
  elseif address:match("^/track/(%d+)/solo$") and #args >= 1 then
    local track_id = tonumber(address:match("^/track/(%d+)/solo$"))
    local solo = tonumber(args[1])
    if track_id and solo ~= nil then
      local track = reaper.GetTrack(0, track_id - 1)  -- Convert to 0-based
      if track then
        reaper.SetMediaTrackInfo_Value(track, "I_SOLO", solo)
      end
    end
    
  -- Query operations
  elseif address == "/query/track_count" then
    local count = reaper.CountTracks(0)
    send_osc_message("/response/track_count", count)
    
  elseif address == "/query/play_state" then
    local state = reaper.GetPlayState()
    send_osc_message("/response/play_state", state)
    
  elseif address == "/query/time_position" then
    local pos = reaper.GetCursorPosition()
    send_osc_message("/response/time_position", pos)
    
  elseif address == "/query/beat_position" then
    local time_pos = reaper.GetCursorPosition()
    local beat_pos = reaper.TimeMap2_timeToBeats(0, time_pos)
    send_osc_message("/response/beat_position", beat_pos)
    
  elseif address == "/ping" then
    send_osc_message("/response/pong", "pong")
    
  -- MIDI Note operations
  elseif address:match("^/track/(%d+)/note_on$") and #args >= 2 then
    local track_id = tonumber(address:match("^/track/(%d+)/note_on$"))
    local pitch = tonumber(args[1])
    local velocity = tonumber(args[2])
    local channel = tonumber(args[3]) or 0  -- Default to channel 0
    if track_id and pitch and velocity then
      local track = reaper.GetTrack(0, track_id - 1)  -- Convert to 0-based
      if track then
        -- Ensure track is properly configured for Virtual MIDI Keyboard
        local rec_input = reaper.GetMediaTrackInfo_Value(track, "I_RECINPUT")
        if rec_input ~= 6112 then
          log("Track " .. track_id .. " input was " .. rec_input .. ", setting to Virtual MIDI Keyboard (6112)")
          reaper.SetMediaTrackInfo_Value(track, "I_RECINPUT", 6112)
        end
        
        -- Ensure track is record armed
        local rec_arm = reaper.GetMediaTrackInfo_Value(track, "I_RECARM")
        if rec_arm ~= 1 then
          reaper.SetMediaTrackInfo_Value(track, "I_RECARM", 1)
        end
        
        -- Ensure input monitoring is on
        local rec_mon = reaper.GetMediaTrackInfo_Value(track, "I_RECMON")
        if rec_mon ~= 1 then
          reaper.SetMediaTrackInfo_Value(track, "I_RECMON", 1)
        end
        
        -- Send MIDI note on directly to track
        local msg1 = 0x90 | channel  -- Note on + channel
        local msg2 = pitch
        local msg3 = velocity
        
        -- Use StuffMIDIMessage to virtual input
        reaper.StuffMIDIMessage(0, msg1, msg2, msg3)
        
        -- Update track display
        reaper.TrackList_AdjustWindows(false)
        reaper.UpdateArrange()
        
        log("Sent MIDI Note On: Track " .. track_id .. ", Pitch " .. pitch .. ", Velocity " .. velocity .. " (Channel " .. channel .. ")")
      else
        log("ERROR: Track " .. track_id .. " not found!")
      end
    end
    
  elseif address:match("^/track/(%d+)/note_off$") and #args >= 1 then
    local track_id = tonumber(address:match("^/track/(%d+)/note_off$"))
    local pitch = tonumber(args[1])
    local channel = tonumber(args[2]) or 0  -- Default to channel 0
    if track_id and pitch then
      local track = reaper.GetTrack(0, track_id - 1)  -- Convert to 0-based
      if track then
        -- Send MIDI note off directly to track
        local msg1 = 0x80 | channel  -- Note off + channel
        local msg2 = pitch
        local msg3 = 0  -- Release velocity
        
        reaper.StuffMIDIMessage(0, msg1, msg2, msg3)
        reaper.TrackList_AdjustWindows(false)
        reaper.UpdateArrange()
        
        log("Sent MIDI Note Off: Track " .. track_id .. ", Pitch " .. pitch .. " (Channel " .. channel .. ")")
      else
        log("ERROR: Track " .. track_id .. " not found!")
      end
    end
    
  elseif address:match("^/track/(%d+)/all_notes_off$") then
    local track_id = tonumber(address:match("^/track/(%d+)/all_notes_off$"))
    if track_id then
      local track = reaper.GetTrack(0, track_id - 1)  -- Convert to 0-based
      if track then
        -- Send All Notes Off (CC 123)
        for channel = 0, 15 do
          reaper.StuffMIDIMessage(0, 0xB0 | channel, 123, 0)
        end
        log("Sent All Notes Off: Track " .. track_id)
      end
    end
    
  else
    log("Unknown OSC address: " .. address)
  end
end

-- Check for incoming OSC messages
function check_osc_messages()
  if not OSC_ENABLED then
    return
  end
  
  -- Check for OSC messages in ExtState (fallback method)
  -- Use global ExtState, not project ExtState!
  local raw_value = reaper.GetExtState("reaside_osc", "incoming")
  if raw_value and raw_value ~= "" then
    log("Found OSC message in ExtState: " .. raw_value)
    
    -- Clear the message immediately
    reaper.DeleteExtState("reaside_osc", "incoming", false)
    
    -- Parse the JSON message
    log("About to parse JSON...")
    local osc_message = parse_json(raw_value)
    
    if osc_message then
      log("JSON parsed successfully, type: " .. type(osc_message))
      if type(osc_message) == "table" then
        log("Message is table, checking for address...")
        if osc_message.address then
          log("Found address: " .. tostring(osc_message.address))
          log("About to handle OSC message...")
          handle_osc_message(osc_message.address, osc_message.args or {})
          log("OSC message handled")
        else
          log("ERROR: No address field in message")
        end
      else
        log("ERROR: Parsed message is not a table")
      end
    else
      log("ERROR: Failed to parse JSON")
    end
  end
end

-- Send periodic updates via OSC
function send_osc_updates()
  if not OSC_ENABLED then
    return
  end
  
  -- Send transport state changes
  local current_transport_state = reaper.GetPlayState()
  if current_transport_state ~= last_transport_state then
    if current_transport_state == 0 then
      send_osc_message("/transport/stop")
    elseif current_transport_state == 1 then
      send_osc_message("/transport/play")
    elseif current_transport_state == 2 then
      send_osc_message("/transport/pause")
    elseif current_transport_state == 5 then
      send_osc_message("/transport/record", 1)
    elseif current_transport_state == 6 then
      send_osc_message("/transport/record", 0)  -- Record paused
    end
    last_transport_state = current_transport_state
  end
  
  -- Send time position updates (every second to avoid spam)
  local current_time = reaper.GetCursorPosition()
  if math.abs(current_time - last_time_position) > 0.1 then  -- Update if >100ms change
    send_osc_message("/time/position", current_time)
    last_time_position = current_time
    
    -- Also send beat position
    local beat_pos = reaper.TimeMap2_timeToBeats(0, current_time)
    if math.abs(beat_pos - last_beat_position) > 0.01 then
      send_osc_message("/beat/position", beat_pos)
      last_beat_position = beat_pos
    end
  end
end

-- Function to store a userdata pointer and return a unique string ID
function store_pointer(ptr)
  if type(ptr) == "userdata" then
    pointer_counter = pointer_counter + 1
    local ptr_id = "PTR_" .. pointer_counter
    pointer_cache[ptr_id] = ptr
    log("Stored pointer " .. tostring(ptr) .. " as " .. ptr_id)
    return ptr_id
  end
  return ptr
end

-- Function to retrieve a userdata pointer from its string ID
function get_pointer(ptr_id)
  if type(ptr_id) == "string" and ptr_id:sub(1, 4) == "PTR_" then
    local ptr = pointer_cache[ptr_id]
    if ptr then
      log("Retrieved pointer " .. tostring(ptr) .. " from " .. ptr_id)
      return ptr
    else
      log("Warning: Pointer not found for ID " .. ptr_id)
    end
  end
  return ptr_id
end

-- Function to get values from ExtState
function get_ext_state(section, key)
  local value = reaper.GetExtState(section, key)
  if value and value ~= "" then
    -- Try to parse as JSON
    local success, result = pcall(function()
      -- Basic JSON parsing - in real implementation, use a proper JSON parser
      if value:sub(1,1) == "{" or value:sub(1,1) == "[" then
        -- This is a placeholder - actual JSON parsing would be needed
        return value
      end
      return value
    end)
    
    if success then
      return result
    end
    return value
  end
  return nil
end

-- Improved function to convert value to JSON
function to_json(value)
  local json = ""
  local t = type(value)
  
  if t == "nil" then
    json = "null"
  elseif t == "boolean" then
    json = value and "true" or "false"
  elseif t == "number" then
    json = tostring(value)
  elseif t == "string" then
    -- Escape quotes and backslashes
    local escaped = value:gsub('\\', '\\\\'):gsub('"', '\\"')
    json = '"' .. escaped .. '"'
  elseif t == "table" then
    -- Detect if table is an array or object
    local is_array = true
    local max_index = 0
    
    for k, v in pairs(value) do
      if type(k) ~= "number" or k < 1 or math.floor(k) ~= k then
        is_array = false
        break
      end
      max_index = math.max(max_index, k)
    end
    
    if is_array and max_index > 0 then
      -- Handle array
      json = "["
      for i = 1, max_index do
        json = json .. to_json(value[i])
        if i < max_index then
          json = json .. ","
        end
      end
      json = json .. "]"
    else
      -- Handle object
      json = "{"
      local first = true
      for k, v in pairs(value) do
        if not first then
          json = json .. ","
        end
        first = false
        json = json .. '"' .. tostring(k) .. '":' .. to_json(v)
      end
      json = json .. "}"
    end
  else
    -- For anything else (function, userdata, thread), convert to string
    json = '"' .. tostring(value) .. '"'
  end
  
  return json
end

-- Function to set values in ExtState
function set_ext_state(section, key, value, persist)
  local json_value
  
  if type(value) == "table" then
    json_value = to_json(value)
  else
    json_value = tostring(value)
  end
  
  log("Setting ExtState: " .. section .. "/" .. key .. " = " .. json_value)
  reaper.SetExtState(section, key, json_value, persist and 1 or 0)
end

-- Convert REAPER API function name to actual function
function get_reaper_function(name)
  -- First try with reaper. prefix
  local func = reaper[name]
  
  -- If not found, try without prefix
  if not func and _G[name] then
    func = _G[name]
  end
  
  return func
end

-- Scan complete track information including FX and parameters
function scan_track_complete()
  -- Get scan request
  local scan_request = get_ext_state(SECTION, "scan_track_request")
  if not scan_request then
    return
  end
  
  log("Processing track scan request: " .. tostring(scan_request))
  
  -- Parse track index from request
  local track_index = tonumber(scan_request)
  if not track_index then
    log("Invalid track index in scan request")
    set_ext_state(SECTION, "scan_track_result", {
      error = "Invalid track index"
    }, false)
    reaper.DeleteExtState(SECTION, "scan_track_request", false)
    return
  end
  
  -- Get track object
  local track = reaper.GetTrack(0, track_index)
  if not track then
    log("Track not found at index " .. track_index)
    set_ext_state(SECTION, "scan_track_result", {
      error = "Track not found"
    }, false)
    reaper.DeleteExtState(SECTION, "scan_track_request", false)
    return
  end
  
  log("Scanning track at index " .. track_index)
  
  -- Collect track information
  local track_data = {}
  
  -- Basic track info
  local retval, track_name = reaper.GetTrackName(track, "")
  track_data.index = track_index
  track_data.name = track_name
  
  -- Track state
  track_data.volume = reaper.GetMediaTrackInfo_Value(track, "D_VOL")
  track_data.pan = reaper.GetMediaTrackInfo_Value(track, "D_PAN")
  track_data.mute = reaper.GetMediaTrackInfo_Value(track, "B_MUTE") > 0
  track_data.solo = reaper.GetMediaTrackInfo_Value(track, "I_SOLO") > 0
  track_data.rec_arm = reaper.GetMediaTrackInfo_Value(track, "I_RECARM") > 0
  track_data.rec_input = reaper.GetMediaTrackInfo_Value(track, "I_RECINPUT")
  track_data.rec_mode = reaper.GetMediaTrackInfo_Value(track, "I_RECMODE")
  track_data.rec_mon = reaper.GetMediaTrackInfo_Value(track, "I_RECMON")
  
  -- Track color
  track_data.color = reaper.GetTrackColor(track)
  
  -- FX information
  local fx_count = reaper.TrackFX_GetCount(track)
  track_data.fx_count = fx_count
  track_data.fx = {}
  
  log("Track has " .. fx_count .. " FX")
  
  -- Scan each FX
  for fx_idx = 0, fx_count - 1 do
    local fx_info = {}
    
    -- FX name
    local retval, fx_name = reaper.TrackFX_GetFXName(track, fx_idx, "")
    fx_info.index = fx_idx
    fx_info.name = fx_name
    fx_info.enabled = reaper.TrackFX_GetEnabled(track, fx_idx)
    
    -- FX preset
    local retval, preset_name = reaper.TrackFX_GetPreset(track, fx_idx, "")
    fx_info.preset = preset_name
    
    -- Parameter count
    local param_count = reaper.TrackFX_GetNumParams(track, fx_idx)
    fx_info.param_count = param_count
    fx_info.params = {}
    
    log("  FX " .. fx_idx .. ": " .. fx_name .. " (" .. param_count .. " params)")
    
    -- Scan each parameter
    for param_idx = 0, param_count - 1 do
      local param_info = {}
      
      -- Parameter name
      local retval, param_name = reaper.TrackFX_GetParamName(track, fx_idx, param_idx, "", 256)
      param_info.index = param_idx
      param_info.name = param_name
      
      -- Parameter value
      local value = reaper.TrackFX_GetParam(track, fx_idx, param_idx)
      param_info.value = value
      
      -- Parameter range and format
      local retval, minval, maxval = reaper.TrackFX_GetParam(track, fx_idx, param_idx)
      param_info.min = minval
      param_info.max = maxval
      
      -- Get formatted value
      local retval, formatted = reaper.TrackFX_GetFormattedParamValue(track, fx_idx, param_idx, "", 256)
      param_info.formatted = formatted
      
      table.insert(fx_info.params, param_info)
    end
    
    table.insert(track_data.fx, fx_info)
  end
  
  -- Send information
  local send_count = reaper.GetTrackNumSends(track, 0)
  track_data.send_count = send_count
  track_data.sends = {}
  
  log("Track has " .. send_count .. " sends")
  
  -- Scan each send
  for send_idx = 0, send_count - 1 do
    local send_info = {}
    
    send_info.index = send_idx
    
    -- Destination track
    local dest_track = reaper.GetTrackSendInfo_Value(track, 0, send_idx, "P_DESTTRACK")
    if dest_track then
      local retval, dest_name = reaper.GetTrackName(dest_track, "")
      send_info.dest_name = dest_name
      
      -- Find destination track index
      local track_count = reaper.CountTracks(0)
      for i = 0, track_count - 1 do
        if reaper.GetTrack(0, i) == dest_track then
          send_info.dest_index = i
          break
        end
      end
    end
    
    -- Send parameters
    send_info.volume = reaper.GetTrackSendInfo_Value(track, 0, send_idx, "D_VOL")
    send_info.pan = reaper.GetTrackSendInfo_Value(track, 0, send_idx, "D_PAN")
    send_info.mute = reaper.GetTrackSendInfo_Value(track, 0, send_idx, "B_MUTE") > 0
    send_info.phase = reaper.GetTrackSendInfo_Value(track, 0, send_idx, "B_PHASE") > 0
    send_info.mono = reaper.GetTrackSendInfo_Value(track, 0, send_idx, "B_MONO") > 0
    
    table.insert(track_data.sends, send_info)
  end
  
  -- Success response
  local result = {
    success = true,
    track = track_data
  }
  
  set_ext_state(SECTION, "scan_track_result", result, false)
  log("Track scan completed successfully")
  
  -- Clear the request
  reaper.DeleteExtState(SECTION, "scan_track_request", false)
end

-- Execute a ReaScript function from ExtState
function execute_function()
  -- Get function call request
  local request = get_ext_state(SECTION, "function_call")
  if not request then
    -- No function call request found, that's normal
    return
  end
  
  -- Parse the request (simplified JSON parsing)
  local func_name = request:match('"function"%s*:%s*"([^"]+)"')
  if not func_name then
    log("Invalid function call request format")
    set_ext_state(SECTION, "function_result", {
      error = "Invalid function call request format"
    }, false)
    return
  end
  
  -- Get function arguments (improved parsing)
  local args = {}
  local args_str = request:match('"args"%s*:%s*%[([^%]]+)%]')
  log("Args string: " .. tostring(args_str))
  
  if args_str and args_str ~= "" then
    -- First handle the case of empty args array
    if args_str:match('^%s*$') then
      -- Empty args array - nothing to do
    else
      -- Split by commas, but respect quotes and nested structures
      local arg_start = 1
      local in_quotes = false
      local bracket_count = 0
      local brace_count = 0
      
      for i = 1, #args_str do
        local char = args_str:sub(i, i)
        
        if char == '"' and args_str:sub(i-1, i-1) ~= '\\' then
          in_quotes = not in_quotes
        elseif not in_quotes then
          if char == '[' then
            bracket_count = bracket_count + 1
          elseif char == ']' then
            bracket_count = bracket_count - 1
          elseif char == '{' then
            brace_count = brace_count + 1
          elseif char == '}' then
            brace_count = brace_count - 1
          elseif char == ',' and bracket_count == 0 and brace_count == 0 then
            -- Found a comma at the top level - extract the argument
            local arg = args_str:sub(arg_start, i-1)
            arg_start = i + 1
            
            -- Process argument based on type
            local arg_value
            
            -- String (in quotes)
            if arg:match('^%s*".*"%s*$') then
              arg_value = arg:match('^%s*"(.*)"%s*$')
              -- Check if this is a pointer ID and convert it back to userdata
              arg_value = get_pointer(arg_value)
            -- Number
            elseif arg:match('^%s*[%d%.%-]+%s*$') then
              arg_value = tonumber(arg:match('^%s*([%d%.%-]+)%s*$'))
            -- Boolean
            elseif arg:match('^%s*true%s*$') then
              arg_value = true
            elseif arg:match('^%s*false%s*$') then
              arg_value = false
            -- Null/nil
            elseif arg:match('^%s*null%s*$') then
              arg_value = nil
            end
            
            log("Parsed argument: " .. tostring(arg_value))
            table.insert(args, arg_value)
          end
        end
      end
      
      -- Don't forget the last argument
      if arg_start <= #args_str then
        local arg = args_str:sub(arg_start)
        
        -- Process argument based on type
        local arg_value
        
        -- String (in quotes)
        if arg:match('^%s*".*"%s*$') then
          arg_value = arg:match('^%s*"(.*)"%s*$')
          -- Check if this is a pointer ID and convert it back to userdata
          arg_value = get_pointer(arg_value)
        -- Number
        elseif arg:match('^%s*[%d%.%-]+%s*$') then
          arg_value = tonumber(arg:match('^%s*([%d%.%-]+)%s*$'))
        -- Boolean
        elseif arg:match('^%s*true%s*$') then
          arg_value = true
        elseif arg:match('^%s*false%s*$') then
          arg_value = false
        -- Null/nil
        elseif arg:match('^%s*null%s*$') then
          arg_value = nil
        end
        
        log("Parsed argument: " .. tostring(arg_value))
        table.insert(args, arg_value)
      end
    end
  end
  
  log("Number of arguments: " .. #args)
  
  -- Get the function
  local func = get_reaper_function(func_name)
  if not func then
    log("Function not found: " .. func_name)
    set_ext_state(SECTION, "function_result", {
      error = "Function not found: " .. func_name
    }, false)
    return
  end
  
  -- Debug log before execution
  log("Executing function: " .. func_name)
  log("With arguments: ")
  for i, arg in ipairs(args) do
    log("  Arg " .. i .. ": " .. tostring(arg) .. " (type: " .. type(arg) .. ")")
  end
  
  -- Execute the function and capture all return values
  local success, result = pcall(function()
    return {func(table.unpack(args))}  -- Capture all return values in a table
  end)
  
  -- Debug log after execution
  if success then
    log("Function executed successfully: " .. func_name)
    log("Result count: " .. #result)
    for i, val in ipairs(result) do
      log("  Result " .. i .. ": " .. tostring(val) .. " (type: " .. type(val) .. ")")
    end
    
    -- Process each result value for storage
    local processed_results = {}
    for i, val in ipairs(result) do
      if type(val) == "userdata" then
        -- Store userdata pointer in cache and return pointer ID
        processed_results[i] = store_pointer(val)
      elseif type(val) == "thread" or type(val) == "function" then
        -- These types can't be easily serialized, convert to string
        processed_results[i] = tostring(val)
      else
        processed_results[i] = val
      end
    end
    
    -- Format result for storage
    local result_data = {
      success = true,
      result = processed_results
    }
    
    set_ext_state(SECTION, "function_result", result_data, false)
  else
    log("Error executing function: " .. tostring(result))
    set_ext_state(SECTION, "function_result", {
      error = "Error executing function: " .. tostring(result)
    }, false)
  end
  
  -- Clear the request to prevent repeated execution
  reaper.DeleteExtState(SECTION, "function_call", false)
end

-- Initialize the API
function initialize_api()
  log("Initializing reaside HTTP API")
  
  -- Initialize OSC
  local osc_success = init_osc()
  if osc_success then
    log("OSC functionality enabled")
  else
    log("OSC functionality disabled")
  end
  
  -- Store basic information in REAPER's ExtState
  set_ext_state(SECTION, "version", REAPER_VERSION, true)
  set_ext_state(SECTION, "api_status", "ready", true)
  set_ext_state(SECTION, "osc_enabled", OSC_ENABLED and osc_success, true)
  set_ext_state(SECTION, "osc_send_port", OSC_SEND_PORT, true)
  set_ext_state(SECTION, "osc_receive_port", OSC_RECEIVE_PORT, true)
  set_ext_state(SECTION, "last_updated", tostring(os.time()), true)
  
  -- Store the action ID for later use
  local script_path = debug.getinfo(1, "S").source:sub(2)  -- Remove leading @
  local script_name = script_path:match("([^/\\]+)%.lua$")
  
  -- Try multiple ways to find the action ID
  local action_id = 0
  
  -- Method 1: Try looking up by script name pattern
  if script_name then
    local action_name = "_RS" .. script_name:gsub("%.lua$", "")
    action_id = reaper.NamedCommandLookup(action_name)
    log("Trying action name: " .. action_name .. " -> ID: " .. action_id)
  end
  
  -- Method 2: Try looking up registered action from ExtState
  if action_id == 0 then
    local stored_action = get_ext_state(SECTION, "activate_reaside_server")
    if stored_action then
      -- Remove quotes if present
      stored_action = stored_action:gsub('"', '')
      action_id = reaper.NamedCommandLookup(stored_action)
      log("Trying stored action: " .. stored_action .. " -> ID: " .. action_id)
    end
  end
  
  -- Method 3: Try various common patterns
  if action_id == 0 and script_name then
    local patterns = {
      "_" .. script_name:gsub("%.lua$", ""),
      "_RS" .. script_name:gsub("%.lua$", ""):gsub("_", ""),
      script_name:gsub("%.lua$", "")
    }
    
    for _, pattern in ipairs(patterns) do
      action_id = reaper.NamedCommandLookup(pattern)
      if action_id ~= 0 then
        log("Found action with pattern: " .. pattern .. " -> ID: " .. action_id)
        break
      end
    end
  end
  
  if action_id ~= 0 then
    set_ext_state(SECTION, "api_action_id", action_id, true)
    log("Registered API action ID: " .. action_id)
  else
    log("Warning: Could not determine action ID. The script is running but may not be automatically triggerable.")
    log("Script path: " .. tostring(script_path))
    log("Script name: " .. tostring(script_name))
  end
  
  return true
end

-- Run the main loop that checks for function calls
function run_main_loop()
  -- Execute any pending function calls
  execute_function()
  
  -- Execute any pending track scans
  scan_track_complete()
  
  -- Handle OSC communication
  check_osc_messages()
  send_osc_updates()
  
  -- Update timestamps to indicate script is still running
  local current_time = tostring(os.time())
  reaper.SetExtState(SECTION, "last_updated", current_time, false)
  reaper.SetExtState(SECTION, "instance_running", current_time, false)
  
  -- Continue the loop
  reaper.defer(run_main_loop)
end

-- Clean up on exit
function onexit()
  set_ext_state(SECTION, "api_status", "stopped", true)
  reaper.DeleteExtState(SECTION, "function_call", false)
  reaper.DeleteExtState(SECTION, "function_result", false)
  reaper.DeleteExtState(SECTION, "instance_running", false)
  log("reaside API Bridge stopped")
end

-- Register exit handler
reaper.atexit(onexit)

-- Main function
function main()
  -- Check if script is already running by checking the instance lock
  local instance_lock = reaper.GetExtState(SECTION, "instance_running")
  local current_time = os.time()
  
  if instance_lock and instance_lock ~= "" then
    -- Try to parse the timestamp from the lock
    local lock_time = tonumber(instance_lock) or 0
    local time_diff = current_time - lock_time
    
    -- If the lock is recent (less than 10 seconds old), assume another instance is running
    if time_diff < 10 then
      reaper.ShowMessageBox("Another instance of the reaside API bridge is already running.\n\nOnly one instance should be active at a time.", "reaside Warning", 0)
      return
    else
      -- Lock is old, assume crashed/stale instance
      log("Found stale instance lock. Proceeding anyway.")
    end
  end
  
  -- Set instance lock
  reaper.SetExtState(SECTION, "instance_running", tostring(current_time), false)
  
  -- Initialize the API
  local success = initialize_api()
  if not success then
    reaper.ShowMessageBox("Failed to initialize reaside HTTP API.", "reaside Error", 0)
    -- Clear instance lock if initialization failed
    reaper.DeleteExtState(SECTION, "instance_running", false)
    return
  end
  
  -- Show confirmation message
  reaper.ShowConsoleMsg("reaside HTTP API Bridge initialized and running!\n")
  reaper.ShowConsoleMsg("REAPER version: " .. REAPER_VERSION .. "\n")
  reaper.ShowConsoleMsg("Keep this script running for reaside to work.\n")
  
  -- Start the continuous monitoring loop
  run_main_loop()
end

-- Start everything
main()