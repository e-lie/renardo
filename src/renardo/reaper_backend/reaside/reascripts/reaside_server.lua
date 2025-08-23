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
local DEBUG = false  -- Set to true to enable debug logging
local SECTION = "reaside"
local REAPER_VERSION = reaper.GetAppVersion()

-- Pointer cache to store userdata objects (MediaTrack, MediaItem, etc.)
local pointer_cache = {}
local pointer_counter = 0

-- Debug logging function
function log(msg)
  if DEBUG then
    reaper.ShowConsoleMsg("[reaside] " .. tostring(msg) .. "\n")
  end
end

-- Simple JSON parser (handles basic cases)
function parse_json(str)
  if not str or str == "" then
    return nil
  end
  
  -- Remove whitespace
  str = str:gsub("^%s*", ""):gsub("%s*$", "")
  
  -- Try to parse as a Lua table using loadstring
  local func, err = loadstring("return " .. str)
  if func then
    local success, result = pcall(func)
    if success then
      return result
    end
  end
  
  -- Fallback: Try converting JSON-like syntax to Lua
  -- Replace JSON syntax with Lua syntax
  local lua_str = str
    :gsub('"(%w+)"%s*:', '["%1"]=')  -- "key": -> ["key"]=
    :gsub(':%s*"', '="')              -- : " -> ="
    :gsub(':%s*([%d%.%-]+)', '=%1')  -- : number -> =number
    :gsub(':%s*true', '=true')       -- : true -> =true
    :gsub(':%s*false', '=false')     -- : false -> =false
    :gsub(':%s*null', '=nil')        -- : null -> =nil
    :gsub(':%s*%[', '={')             -- : [ -> ={
    :gsub('%]', '}')                  -- ] -> }
  
  -- Try parsing the converted string
  func, err = loadstring("return " .. lua_str)
  if func then
    local success, result = pcall(func)
    if success then
      return result
    end
  end
  
  log("Failed to parse JSON: " .. tostring(err))
  return nil
end

-- Handle incoming JSON messages
function handle_json_message(address, args)
  log("Received message: " .. address .. " with " .. #args .. " args")
  
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
    
  -- Query operations removed - part of unused OSC system
    
  elseif address == "/ping" then
    -- Ping/pong removed - was part of unused OSC system
    
  -- TEST CUSTOM FUNCTION - REMOVE AFTER TESTING
  elseif address == "/custom/test_function" then
    -- Simple test function that just logs a message
    local test_message = "Custom function triggered!"
    
    -- If args provided, include them in the message
    if args and #args > 0 then
      test_message = test_message .. " Args: " .. table.concat(args, ", ")
    end
    
    -- Show in Reaper console
    reaper.ShowConsoleMsg("[CUSTOM TEST] " .. test_message .. "\n")
    
    -- Also log it (only visible if DEBUG = true)
    log("Custom function executed: " .. test_message)
    
  else
    log("Unknown message address: " .. address)
  end
end

-- Check for incoming JSON messages via ExtState
function check_json_messages()
  -- Check for messages in ExtState
  -- Use global ExtState, not project ExtState!
  local raw_value = reaper.GetExtState("reaside_json", "incoming")
  if raw_value and raw_value ~= "" then
    log("Found JSON message in ExtState: " .. raw_value)
    
    -- Clear the message immediately
    reaper.DeleteExtState("reaside_json", "incoming", false)
    
    -- Parse the JSON message
    log("About to parse JSON...")
    local json_message = parse_json(raw_value)
    
    if json_message then
      log("JSON parsed successfully, type: " .. type(json_message))
      if type(json_message) == "table" then
        log("Message is table, checking for address...")
        if json_message.address then
          log("Found address: " .. tostring(json_message.address))
          log("About to handle message...")
          handle_json_message(json_message.address, json_message.args or {})
          log("Message handled")
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

-- Removed send_osc_updates function - part of unused OSC system

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

-- Save FX chain from a track to a file
function save_fxchain()
  -- Get save request
  local save_request = get_ext_state(SECTION, "save_fxchain_request")
  if not save_request then
    return
  end
  
  log("Processing save FX chain request: " .. tostring(save_request))
  
  -- Parse the request - expect JSON like {"track_index": 0, "file_path": "/path/to/file.RfxChain"}
  local track_index = save_request:match('"track_index"%s*:%s*(%d+)')
  local file_path = save_request:match('"file_path"%s*:%s*"([^"]+)"')
  
  if not track_index or not file_path then
    log("Invalid save FX chain request format")
    set_ext_state(SECTION, "save_fxchain_result", {
      error = "Invalid request format"
    }, false)
    reaper.DeleteExtState(SECTION, "save_fxchain_request", false)
    return
  end
  
  track_index = tonumber(track_index)
  
  -- Get track object
  local track = reaper.GetTrack(0, track_index)
  if not track then
    log("Track not found at index " .. track_index)
    set_ext_state(SECTION, "save_fxchain_result", {
      error = "Track not found"
    }, false)
    reaper.DeleteExtState(SECTION, "save_fxchain_request", false)
    return
  end
  
  -- Check if track has FX
  local fx_count = reaper.TrackFX_GetCount(track)
  if fx_count == 0 then
    log("No FX on track to save")
    set_ext_state(SECTION, "save_fxchain_result", {
      error = "No FX on track"
    }, false)
    reaper.DeleteExtState(SECTION, "save_fxchain_request", false)
    return
  end
  
  -- Get track state chunk
  local retval, chunk = reaper.GetTrackStateChunk(track, "", 16384, false)
  if not retval then
    log("Failed to get track state chunk")
    set_ext_state(SECTION, "save_fxchain_result", {
      error = "Failed to get track chunk"
    }, false)
    reaper.DeleteExtState(SECTION, "save_fxchain_request", false)
    return
  end
  
  -- Extract FX section from chunk
  log("Extracting FXCHAIN section from track chunk")
  log("Chunk length: " .. #chunk)
  
  local fx_section = ""
  local fxchain_start = chunk:find("<FXCHAIN")
  
  if not fxchain_start then
    log("No FXCHAIN section found in track chunk")
    set_ext_state(SECTION, "save_fxchain_result", {
      error = "No FXCHAIN section found"
    }, false)
    reaper.DeleteExtState(SECTION, "save_fxchain_request", false)
    return
  end
  
  log("Found FXCHAIN at position: " .. fxchain_start)
  
  -- Find the matching closing > for the FXCHAIN section
  local pos = fxchain_start + 8 -- Start after "<FXCHAIN"
  local depth = 1
  local fxchain_end = nil
  
  while pos <= #chunk do
    local char = chunk:sub(pos, pos)
    if char == '<' then
      depth = depth + 1
    elseif char == '>' then
      depth = depth - 1
      if depth == 0 then
        -- Found the closing > for the FXCHAIN
        fxchain_end = pos
        log("Found FXCHAIN end at position: " .. fxchain_end)
        break
      end
    end
    pos = pos + 1
  end
  
  if not fxchain_end then
    log("Could not find end of FXCHAIN section")
    set_ext_state(SECTION, "save_fxchain_result", {
      error = "Could not parse FXCHAIN section"
    }, false)
    reaper.DeleteExtState(SECTION, "save_fxchain_request", false)
    return
  end
  
  -- For .RfxChain format, we need just the inner content (without <FXCHAIN> tags)
  -- Find the first newline after <FXCHAIN to get the inner content start
  local newline_after_fxchain = chunk:find("\n", fxchain_start)
  if not newline_after_fxchain then
    log("Could not find content after FXCHAIN tag")
    set_ext_state(SECTION, "save_fxchain_result", {
      error = "Invalid FXCHAIN format"
    }, false)
    reaper.DeleteExtState(SECTION, "save_fxchain_request", false)
    return
  end
  
  -- Extract inner content (everything between <FXCHAIN\n and the final >)
  local inner_start = newline_after_fxchain + 1
  local inner_end = fxchain_end - 1
  
  -- Skip the final newline if present
  while inner_end > inner_start and (chunk:sub(inner_end, inner_end) == '\n' or chunk:sub(inner_end, inner_end) == '\r') do
    inner_end = inner_end - 1
  end
  
  fx_section = chunk:sub(inner_start, inner_end)
  
  -- Validate that we have some content
  if not fx_section or fx_section:match("^%s*$") then
    log("FXCHAIN section is empty")
    set_ext_state(SECTION, "save_fxchain_result", {
      error = "Empty FXCHAIN section"
    }, false)
    reaper.DeleteExtState(SECTION, "save_fxchain_request", false)
    return
  end
  
  log("Extracted FX section length: " .. #fx_section)
  log("FX section preview: " .. fx_section:sub(1, 100) .. "...")
  
  -- Write to file
  local file = io.open(file_path, "w")
  if file then
    file:write(fx_section)
    file:close()
    log("FX chain saved to " .. file_path)
    set_ext_state(SECTION, "save_fxchain_result", {
      success = true
    }, false)
  else
    log("Failed to write FX chain file")
    set_ext_state(SECTION, "save_fxchain_result", {
      error = "Failed to write file"
    }, false)
  end
  
  -- Clear the request
  reaper.DeleteExtState(SECTION, "save_fxchain_request", false)
end

-- Helper function to add chunk to track (based on ReaperIntegrationLib)
function add_chunk_to_track(track, chunk_content)
  log("Adding chunk to track")
  
  local retval, track_xml_chunk = reaper.GetTrackStateChunk(track, "", 999999, false)
  if not retval then
    log("Failed to get track state chunk")
    return false
  end
  
  log("Original track chunk length: " .. #track_xml_chunk)
  
  -- Add empty FX chain if it doesn't exist
  if not track_xml_chunk:find("FXCHAIN") then
    log("Track has no FXCHAIN - adding empty one")
    -- Insert empty FXCHAIN before the closing >
    track_xml_chunk = track_xml_chunk:gsub("(.*)(>\n*)$", "%1\n<FXCHAIN\nSHOW 0\nLASTSEL 0\nDOCKED 0\n>\n%2")
  end
  
  -- Add the chunk content after DOCKED 0
  if chunk_content and chunk_content ~= "" then
    log("Adding content after DOCKED 0")
    track_xml_chunk = track_xml_chunk:gsub("DOCKED 0", "DOCKED 0\n" .. chunk_content)
  end
  
  log("Modified track chunk length: " .. #track_xml_chunk)
  
  -- Set the modified chunk back to the track
  local set_result = reaper.SetTrackStateChunk(track, track_xml_chunk, false)
  log("SetTrackStateChunk result: " .. tostring(set_result))
  
  return set_result
end

-- Helper function to move FX from one track to another (based on ReaperIntegrationLib)
function move_fx(source_track, dest_track)
  log("Moving FX from source track to destination track")
  
  local fx_count = reaper.TrackFX_GetCount(source_track)
  log("Source track has " .. fx_count .. " FX to move")
  
  local moved_count = 0
  
  -- Move each FX from source to destination in correct order
  for i = 0, fx_count - 1 do
    local success = reaper.TrackFX_CopyToTrack(source_track, i, dest_track, i, false)
    if success then
      log("Moved FX " .. i .. " to position " .. i .. " successfully")
      moved_count = moved_count + 1
    else
      log("Failed to move FX " .. i)
    end
  end
  
  -- Now delete all FX from source track (backwards to avoid index issues)
  for i = fx_count - 1, 0, -1 do
    reaper.TrackFX_Delete(source_track, i)
  end
  
  log("Moved " .. moved_count .. " FX total")
  return moved_count
end

-- Add FX chain from a file to a track (based on ReaperIntegrationLib approach)
function add_fxchain()
  -- Get add request
  local add_request = get_ext_state(SECTION, "add_fxchain_request")
  if not add_request then
    return
  end
  
  log("Processing add FX chain request: " .. tostring(add_request))
  
  -- Parse the request - expect JSON like {"track_index": 0, "file_path": "/path/to/file.RfxChain"}
  local track_index = add_request:match('"track_index"%s*:%s*(%d+)')
  local file_path = add_request:match('"file_path"%s*:%s*"([^"]+)"')
  
  if not track_index or not file_path then
    log("Invalid add FX chain request format")
    set_ext_state(SECTION, "add_fxchain_result", {
      error = "Invalid request format"
    }, false)
    reaper.DeleteExtState(SECTION, "add_fxchain_request", false)
    return
  end
  
  track_index = tonumber(track_index)
  
  -- Get target track object
  local target_track = reaper.GetTrack(0, track_index)
  if not target_track then
    log("Track not found at index " .. track_index)
    set_ext_state(SECTION, "add_fxchain_result", {
      error = "Track not found"
    }, false)
    reaper.DeleteExtState(SECTION, "add_fxchain_request", false)
    return
  end
  
  -- Get FX count before adding the chain
  local fx_count_before = reaper.TrackFX_GetCount(target_track)
  log("Target track has " .. fx_count_before .. " FX initially")
  
  -- Read the FX chain file
  local file = io.open(file_path, "r")
  if not file then
    log("Failed to read FX chain file: " .. file_path)
    set_ext_state(SECTION, "add_fxchain_result", {
      error = "Failed to read FX chain file"
    }, false)
    reaper.DeleteExtState(SECTION, "add_fxchain_request", false)
    return
  end
  
  local chain_content = file:read("*all")
  file:close()
  
  if not chain_content or chain_content == "" then
    log("FX chain file is empty")
    set_ext_state(SECTION, "add_fxchain_result", {
      error = "FX chain file is empty"
    }, false)
    reaper.DeleteExtState(SECTION, "add_fxchain_request", false)
    return
  end
  
  log("Chain content length: " .. #chain_content)
  log("Chain content preview: " .. chain_content:sub(1, 100) .. "...")
  
  -- Use ReaperIntegrationLib approach: create temporary track and move FX
  log("Creating temporary track for FX chain loading")
  
  -- Prevent UI refresh during operation
  reaper.PreventUIRefresh(1)
  
  -- Add empty track at the end to instantiate chain
  local track_count = reaper.CountTracks(0)
  reaper.InsertTrackAtIndex(track_count, false)
  local temp_track = reaper.GetTrack(0, track_count)  -- New track is at the end
  
  if not temp_track then
    log("Failed to create temporary track")
    reaper.PreventUIRefresh(-1)
    set_ext_state(SECTION, "add_fxchain_result", {
      error = "Failed to create temporary track"
    }, false)
    reaper.DeleteExtState(SECTION, "add_fxchain_request", false)
    return
  end
  
  log("Created temporary track")
  
  -- Add chain via XML chunk format to temporary track
  local chunk_success = add_chunk_to_track(temp_track, chain_content)
  if not chunk_success then
    log("Failed to add chunk to temporary track")
    reaper.DeleteTrack(temp_track)
    reaper.PreventUIRefresh(-1)
    set_ext_state(SECTION, "add_fxchain_result", {
      error = "Failed to add chunk to temporary track"
    }, false)
    reaper.DeleteExtState(SECTION, "add_fxchain_request", false)
    return
  end
  
  -- Check how many FX were loaded on the temporary track
  local temp_fx_count = reaper.TrackFX_GetCount(temp_track)
  log("Temporary track has " .. temp_fx_count .. " FX after loading chain")
  
  -- Move FX from temporary track to target track
  local moved_fx_count = 0
  if temp_fx_count > 0 then
    moved_fx_count = move_fx(temp_track, target_track)
  end
  
  -- Remove the temporary track
  reaper.DeleteTrack(temp_track)
  
  -- Re-enable UI refresh
  reaper.PreventUIRefresh(-1)
  
  -- Get final FX count
  local fx_count_after = reaper.TrackFX_GetCount(target_track)
  local fx_added = fx_count_after - fx_count_before
  
  log("FX chain process completed:")
  log("  FX count before: " .. fx_count_before)
  log("  FX count after: " .. fx_count_after)
  log("  FX added: " .. fx_added)
  log("  FX moved from temp track: " .. moved_fx_count)
  
  -- List the FX that are now on the target track
  if fx_count_after > 0 then
    log("Current FX on target track:")
    for i = 0, fx_count_after - 1 do
      local retval, fx_name = reaper.TrackFX_GetFXName(target_track, i, "", 256)
      log("  FX " .. i .. ": " .. tostring(fx_name))
    end
  else
    log("No FX found on target track after adding chain")
  end
  
  -- Success response
  set_ext_state(SECTION, "add_fxchain_result", {
    success = true,
    fx_added = fx_added,
    fx_count_before = fx_count_before,
    fx_count_after = fx_count_after,
    temp_fx_count = temp_fx_count,
    moved_fx_count = moved_fx_count
  }, false)
  
  -- Clear the request
  reaper.DeleteExtState(SECTION, "add_fxchain_request", false)
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
  
  -- Removed OSC initialization - using ExtState JSON messages instead
  
  -- Store basic information in REAPER's ExtState
  set_ext_state(SECTION, "version", REAPER_VERSION, true)
  set_ext_state(SECTION, "api_status", "ready", true)
  -- Removed OSC configuration storage
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
  
  -- Execute any pending FX chain operations
  save_fxchain()
  add_fxchain()
  
  -- Handle JSON messages via ExtState
  check_json_messages()
  
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
  log("reaside HTTP API Bridge initialized and running!")
  log("REAPER version: " .. REAPER_VERSION)
  log("Keep this script running for reaside to work.")
  
  -- Start the continuous monitoring loop
  run_main_loop()
end

-- Start everything
main()