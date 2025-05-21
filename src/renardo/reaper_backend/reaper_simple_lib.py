import reapy
from reapy import Project, RPR


def calculate_track_idx(track_num):
    project_idx=0 # 0 is currently active project
    track_count = RPR.CountTracks(project_idx)
    track_index = 0
    if track_num < 0: # -1 for last track -2 for the one before etc
        track_index = track_count + track_num
        track_index = max(track_index, 0) # minimum 0
    else:
        track_index = track_num
        track_index = min(track_count-1, track_num) # maximum track count -1
        track_index = max(track_index, 0) # minimum 0
    return track_index


def get_track(track_num):
    project_idx=0 # 0 is currently active project
    return RPR.GetTrack(project_idx, calculate_track_idx(track_num))

def get_master_track():
    project_idx=0 # 0 is currently active project
    return RPR.GetMasterTrack(project_idx)

def ensure_track(track_or_num):
    track = track_or_num
    if isinstance(track_or_num, int):
        track = get_track(track_or_num)
        return track
    return track

def rename_track(track_name, track=None, track_num=-1):
    set_new_value = True
    if not track:
        track = get_track(track_num)
    parameter_name = "P_NAME"
    RPR.GetSetMediaTrackInfo_String(track, parameter_name, track_name, set_new_value)


def add_track(track_name="", track_num=-1):
    project_idx=0 # 0 is currently active project
    want_defaults = False
    track_idx = calculate_track_idx(track_num)
    if track_num == -1:
        track_idx += 1 # if track_num is -1 we add the track after everything not before the last track
    RPR.InsertTrackAtIndex(track_idx, want_defaults)
    new_track = get_track(track_idx)
    if track_name:
        rename_track(track_name, new_track)
    return new_track


def track_volume(track_or_num, volume):
    track = ensure_track(track_or_num)
    RPR.SetMediaTrackInfo_Value(track, "D_VOL", float(volume))

def master_volume(volume):
    master_track = get_master_track()
    RPR.SetMediaTrackInfo_Value(master_track, "D_VOL", volume)

def midi_selection_idx(midi_device=0, midi_chan=0, all_midi_inputs=False):
    """
    Calculate the MIDI input selection index for REAPER.
    
    Args:
        midi_device: Index of MIDI device (0 = first device, 1 = second device, etc.)
                     Ignored if all_midi_inputs is True.
        midi_chan: MIDI channel (1-16), or -1 for all channels
        all_midi_inputs: When True, use "All MIDI inputs" instead of a specific device
    
    Returns:
        int: The calculated index for REAPER's I_RECINPUT parameter
    """
    if midi_chan == -1:  # -1 means all channels
        channel_idx = 0
    else:
        channel_idx = max(midi_chan, 1)  # Ensure valid channel (minimum 1)
    
    if all_midi_inputs:
        # For "All MIDI inputs", use device index 63 (0x3F)
        device_idx = 63  # Special value for "All MIDI inputs"
    else:
        device_idx = midi_device
    
    idx = 4096 + (device_idx << 5) + channel_idx  # Magic REAPER formula
    return idx

def track_midi_input(track_or_num, midi_chan, midi_device=0, all_midi_inputs=True):
    """
    Set the MIDI input for a track.
    
    Args:
        track_or_num: Track object or track index
        midi_chan: MIDI channel (1-16), or -1 for all channels
        midi_device: Index of MIDI device (0 = first device, 1 = second device, etc.)
                     Ignored if all_midi_inputs is True.
        all_midi_inputs: When True, use "All MIDI inputs" instead of a specific device
    """
    track = ensure_track(track_or_num)
    RPR.SetMediaTrackInfo_Value(track, "I_RECINPUT", 
                               midi_selection_idx(midi_device, midi_chan, all_midi_inputs))

def add_send(src_track_or_num, dest_track_or_num, volume=1.0, mode="post_fader"):
    if mode == "pre_fx":
        mode_idx = 0
    elif mode == "post_fx":
        mode_idx = 1
    elif mode == "post_fader":
        mode_idx = 3
    else:
        raise Exception("wrong send mode : choose between post_fader, pre_fx or post_fx")
    src_track = ensure_track(src_track_or_num)
    dest_track = ensure_track(dest_track_or_num)
    send_idx = RPR.CreateTrackSend(src_track, dest_track)
    send_category = 0
    # set volume
    RPR.SetTrackSendInfo_Value(src_track, send_category, send_idx, "D_VOL", volume)
    # set send mode
    RPR.SetTrackSendInfo_Value(src_track, send_category, send_idx, "I_SENDMODE", mode_idx)
    

def set_send_volume(track_or_num, send_idx=0, volume=1.0):
    track = ensure_track(track_or_num)
    send_category = 0
    RPR.SetTrackSendInfo_Value(track, send_category, send_idx, "D_VOL", volume)


def db_to_volume(dB):
    return 10 ** (dB / 20.0)


def arm_track(track_or_num):
    track = ensure_track(track_or_num)
    RPR.SetMediaTrackInfo_Value(track, "I_RECARM", 1)

def unarm_track(track_or_num):
    track = ensure_track(track_or_num)
    RPR.SetMediaTrackInfo_Value(track, "I_RECARM", 0)

# set_send_volume(1,0,db_to_volume(-3))

# master_volume(db_to_volume(-2))

# unarm_track(0)


def create_standard_midi_track(track_num: int):
    """
    Create a MIDI track for renardo integration

    The track is:
    - Named chan1 to 16 from track_num
    - Record armed
    - Set to receive from "All MIDI inputs"
    - Set to receive from the MIDI channel corresponding to its number
    - Record mode set to "Stereo Out" (monitors the track output)
    """
    # Create track with name "chanX" where X is the channel number
    track_name = f"chan{track_num}"
    track = add_track(track_name)
    
    # Set MIDI input to "All MIDI inputs" on the appropriate channel
    track_midi_input(track, track_num)  # This sets the input to the corresponding channel number
    
    # Arm the track for recording
    arm_track(track)
    
    # Set record mode to "2 = None (disables recording)"
    set_record_mode(track, 2)

def set_record_mode(track_or_num, mode, output_point=None):
    """
    Set the record mode for a track.
    
    Args:
        track_or_num: Track object or track index
        mode: Record mode (integer value):
            0 = Input (records from track input)
            1 = Stereo Out (records output of track)
            2 = None (disables recording)
            3 = Stereo Out with latency compensation
            4 = MIDI Output
            5 = Mono Out
            6 = Mono Out with latency compensation
            7 = MIDI Overdub
            8 = MIDI Replace
        output_point: Output point for recording (only relevant for output recording modes):
            None = Don't change output point 
            "post-fader" = Post-fader (default in REAPER)
            "pre-fx" = Pre-FX
            "post-fx" = Post-FX/Pre-fader
    """
    track = ensure_track(track_or_num)
    
    # Set the basic record mode
    RPR.SetMediaTrackInfo_Value(track, "I_RECMODE", mode)
    
    # Set the output recording point if specified
    if output_point is not None:
        # Get current flags
        current_flags = RPR.GetMediaTrackInfo_Value(track, "I_RECMODE_FLAGS")
        
        # Clear the first 2 bits that define output point
        flags = current_flags & ~3
        
        # Set new output point
        if output_point == "pre-fx":
            flags |= 1
        elif output_point == "post-fx":
            flags |= 2
        # "post-fader" is 0, so no bits need to be set
        
        # Update the flags
        RPR.SetMediaTrackInfo_Value(track, "I_RECMODE_FLAGS", flags)


def create_16_midi_tracks():
    """
    Creates 16 MIDI tracks in REAPER, one for each MIDI channel.
    """  
    # Create 16 tracks, one for each MIDI channel
    for i in range(1, 17):  # 1 to 16
        create_standard_midi_track(i)


def ensure_16_midi_tracks():
    """
    Ensures that 16 MIDI tracks exist in REAPER, one for each MIDI channel.
    Only creates tracks that don't already exist, making it idempotent.
    
    Returns:
        list: List of track indices that were created (empty if all already existed)
    """
    project_idx = 0  # 0 is currently active project
    track_count = RPR.CountTracks(project_idx)
    
    # Check which channels already have tracks
    existing_channels = set()
    for i in range(track_count):
        track = RPR.GetTrack(project_idx, i)
        name = RPR.GetTrackName(track, "", 512)[2].strip()
        
        # Check if this is a channel track (expected format: "chanX" where X is 1-16)
        if name.startswith("chan") and len(name) > 4:
            try:
                channel_num = int(name[4:])
                if 1 <= channel_num <= 16:
                    existing_channels.add(channel_num)
            except ValueError:
                # If we can't convert to int, it's not a proper channel track
                pass
    
    # Create only the missing tracks
    created_tracks = []
    for i in range(1, 17):  # 1 to 16
        if i not in existing_channels:
            create_standard_midi_track(i)
            created_tracks.append(i)
    
    return created_tracks