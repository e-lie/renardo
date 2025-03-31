from renardo.lib.runtime import Clock, nextBar, inf, linvar
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
    Clock.bpm = linvar([Clock.bpm, bpm], [dur,inf], start=Clock.mod(4))
    @nextBar(dur)
    def adjust_reaper_bpm():
        reaproject.bpm = bpm
        


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