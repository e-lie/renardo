"""
This script tests the fixed PersistentPointInTime implementation with both
direct scheduling and derived points (+16).
"""

# First clear all music
Clock.clear()

# Create a persistent point for chorus sections
somebreak = ppit()  # or PersistentPointInTime()

# Start some musical loop
Clock.bpm = 160
print("Starting music loop...")
b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6])
k2 >> play("v.(.x)(v*)*v.", dur=.25)
d2 >> play("{cccc.}", dur=var([2, 2/3], [12, 4]), rate=(1.2, 2.4), lpf=800)

# Functions for the break
def cut_drums():
    print(f"\n>>> CUTTING DRUMS at beat {Clock.now()}")
    d2.amplify = 0  # break (cutting the drum)
    k2.amplify = 0

def restore_drums():
    print(f"\n>>> RESTORING DRUMS at beat {Clock.now()}")
    d2.amplify = 1
    k2.amplify = 1

# Schedule them
print("Scheduling cut_drums at somebreak")
Clock.schedule(cut_drums, beat=somebreak)

print("Scheduling restore_drums at somebreak+16")
Clock.schedule(restore_drums, beat=somebreak+16)

# First break in 8 beats
print(f"\nTRIGGERING FIRST BREAK at beat now + 8 (current beat: {Clock.now()})")
somebreak.beat = Clock.now() + 8

# Wait for it to run, then try a second break (after 24 beats)
print(f"\n(Try manually triggering a second break after both functions have run with:)")
print("somebreak.beat = Clock.now() + 8")