### Persistent point in time

# A point in time you can reactivate several times (more usefull than single use PointInTime)

# Create a persistent point for chorus sections
somebreak = ppit() # or PersistentPointInTime()

# Start some musical loop
Clock.bpm=160
b1 >> blip([0,1,5,[2,[_,1]]], dur=var([.5,.25],8), sus=1, amp=1.5*P[.4,.7,1,.7], lpf=800, oct=[4,5,6])
k2 >> play("v.(.x)(v*)*v.", dur=.25)
d2 >> play("{cccc.}", dur=var([2,2/3],[12,4]), rate=(1.2,2.4), lpf=800)

# some metronome for fun
p7 >> pluck([4,0,0,0], oct=6, lpf=2000)

# Schedule what happens during break

# {somebreak} cut drums for 16 beats
d2.amplify=0 # break (cutting the drum)
k2.amplify=0
# {somebreak+16} # Put back the drums 16 beats later
d2.amplify=1
k2.amplify=1

# Now you can trigger the break multiple times!

# First break in 16 beats after end of bar (4/4 bar)
somebreak.beat = mod(4) + 16

# Wait a bit, then trigger second break later
somebreak.beat = mod(4) + 32


# Each trigger executes the same musical pattern !

### Recurring point in time (reexecute the code periodically)

# Create a recurring point for hi-hat patterns every 4 beats
hihat_pattern = RecurringPointInTime(period=16)
print(f"Created recurring hi-hat trigger: {hihat_pattern}")

# Schedule the hi-hat pattern
# {hihat_pattern}
hh >> play("--[--]-", dur=1/4, amp=0.4).stop(2)

# Start the recurring pattern
hihat_pattern.beat = now() + 4
print(f"Hi-hat pattern will repeat every 4 beats starting at {Clock.now() + 4}")

# Create a longer recurring pattern for bass drops
drop_cycle = RecurringPointInTime(period=16)

# {drop_cycle}
# Big bass drop every 16 beats
b2 >> bass([0], dur=4, amp=1.5, lpf=400)
d2 >> play("X-------X-------", amp=1.8)

drop_cycle.beat = Clock.now() + 16
print(f"Bass drop will repeat every 16 beats")

# Create a build-up pattern that happens between drops
# {drop_cycle + 8}
# Build-up 8 beats after each drop
p2 >> pluck([0, 2, 4, 7], dur=1/4, amp=var([0.5, 1], 4))
d3 >> play("x-x-x-x-", dur=1/2, amp=0.6)

### Clearing to cancel scheduled events

# All PointInTime classes have a clear() method to remove scheduled operations

# Stop a recurring pattern
reccurent_start_of_drum = rpit(period=8)

# {drum_pattern_to_stop}
d4 >> play("X-o-", dur=1/2)

# Start the pattern
reccurent_start_of_drum.beat = now() + 4

# Later, stop it completely
reccurent_start_of_drum.clear()
print("Drum pattern wont start again with clean()")
