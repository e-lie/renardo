"""
Test script for PersistentPointInTime and derived points
This script demonstrates the fixed implementation
"""

# Create a persistent point for our break sections
somebreak = ppit()  # or PersistentPointInTime()

# Start some musical loop
Clock.bpm = 160
b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6])
k2 >> play("v.(.x)(v*)*v.", dur=.25)
d2 >> play("{cccc.}", dur=var([2, 2/3], [12, 4]), rate=(1.2, 2.4), lpf=800)

# Define and schedule what happens during break - drum muting
def cut_drums():
    print(f">>> Cutting drums at beat {Clock.now()}")
    d2.amplify = 0  # break (cutting the drum)
    k2.amplify = 0
Clock.schedule(cut_drums, beat=somebreak)

# Define and schedule what happens 16 beats after the break - restore drums
def restore_drums():
    print(f">>> Restoring drums at beat {Clock.now()}")
    d2.amplify = 1
    k2.amplify = 1
Clock.schedule(restore_drums, beat=somebreak + 16)

# Use this with FoxDot's live coding environment:

# First break in 8 beats
print(f"Triggering first break at beat {Clock.now() + 8}")
somebreak.beat = Clock.now() + 8

# Wait for the break to finish, then trigger second break
# The second trigger should activate both cut_drums and restore_drums
print(f"Triggering second break at beat {Clock.now() + 8}")
somebreak.beat = Clock.now() + 8

# Note: With the fixed implementation, both the direct break function and
# the +16 restore function will be called on each trigger of somebreak