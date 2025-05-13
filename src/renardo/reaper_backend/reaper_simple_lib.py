
from renardo.reaper_backend.reapy import Project, RPR


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
    track = ensure_track(rack_or_num)
    RPR.SetMediaTrackInfo_Value(track, "D_VOL", float(volume))

def master_volume(volume):
    master_track = get_master_track()
    RPR.SetMediaTrackInfo_Value(master_track, "D_VOL", volume)

def midi_selection_idx(midi_device=0, midi_chan=0):
    if midi_chan == -1: # -1 means all channel
        channel_idx = 0
    else:
        channel_idx = max(midi_chan, 1)
    idx = 4096 + (midi_device << 5) + channel_idx # Magicccc
    return idx

def track_midi_input(track_or_num, midi_chan, midi_device=0):
    track = ensure_track(track_or_num)
    RPR.SetMediaTrackInfo_Value(track, "I_RECINPUT", midi_selection_idx(midi_device, midi_chan))

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

set_send_volume(1,0,db_to_volume(-3))

master_volume(db_to_volume(-2))

unarm_track(0)