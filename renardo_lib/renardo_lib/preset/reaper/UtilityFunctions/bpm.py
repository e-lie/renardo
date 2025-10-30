from renardo_lib import Clock, nextBar, inf, linvar
from renardo_lib.TimeVar import TimeVar
from ..Presets import reaproject, ReaTask

# def change_bpm(bpm, midi_nudge=False, nudge_base=0.72):
#     Clock.bpm = bpm
#     reaproject.bpm = bpm
#     @nextBar()
#     def nudging():
#         if midi_nudge:
#             Clock.midi_nudge = 60 / bpm - nudge_base

def change_bpm(bpm):
    Clock.bpm = bpm

    # Sync with Ableton if available (supports TimeVar)
    try:
        import renardo_lib
        if renardo_lib.ableton_project is not None:
            renardo_lib.ableton_project.change_ableton_bpm(bpm)
    except:
        pass  # Silently ignore if Ableton integration is not available

    # For Reaper: only update with static BPM values (no TimeVar support to avoid queue saturation)
    if not isinstance(bpm, TimeVar):
        @nextBar()
        def change_bpm_reaper():
            reaproject.task_queue.add_task(ReaTask("set_bpm", reaproject, "bpm", float(bpm)))

def change_bpm2(bpm, midi_nudge=True, nudge_base=0.35):
    Clock.bpm = bpm
    reaproject.reapy_project.bpm = bpm
    
    @nextBar()
    def nudging2():
        if midi_nudge:
            Clock.midi_nudge = 120 / bpm - nudge_base

def bpm_to(bpm, dur=8):
    # Create a linvar that transitions from current BPM to target BPM
    bpm_transition = linvar([Clock.bpm, bpm], [dur, inf], start=Clock.mod(4))
    # Use change_bpm to sync Renardo, Reaper, and Ableton
    change_bpm(bpm_transition)

    # After the transition duration, set to the final static BPM
    @nextBar(dur)
    def set_final_bpm():
        change_bpm(bpm)
        


def bpm_to_fadesc(bpm, sc_player, dur=8):
    old_bpm = Clock.bpm
    sc_player.fadeout(4)
    @nextBar()
    def change_it():
        Clock.bpm = linvar([old_bpm, bpm], [dur,inf])
    @nextBar(dur)
    def change_it():
        change_bpm = bpm
        sc_player.fadein(4)