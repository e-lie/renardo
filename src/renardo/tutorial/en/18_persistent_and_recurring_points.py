### Basic PointInTime recap

# Regular PointInTime can only be used once
drop_moment = pit()
b1 >> blip()

# {drop_moment}
p1 >> saw([0], amp=2)
d1 >> play("X---", amp=2)

drop_moment.beat = Clock.now() + 8
# After this triggers, drop_moment is "used up" and can't be triggered again



### Persistent point in time

# Point in time you can reactivate several times (more usefull than)

# Create a persistent point for chorus sections
chorus_start = ppit() # or PersistentPointInTime()

# Start some basic musical loop
p2 >> pluck([0,2,2,5],oct=4)
print(f"Created chorus trigger: {chorus_start}")

# Schedule what happens during chorus (wont start the chorus for now)

# {chorus_start}
p1 >> pluck([0, 2, 4, 2], dur=1/2, amp=0.8).stop(4)
b1 >> bass([0, 0, 2, 2], dur=2, amp=0.6).stop(4)
d1 >> play("X-o-X-o-", dur=1/2).stop(4)

# Now you can trigger the chorus multiple times!

# First chorus at beat 16
chorus_start.beat = now() + 16
print(f"First chorus scheduled at beat {Clock.now() + 16}")
print(f"Chorus state after trigger: {chorus_start}")  # Should be undefined again

# Wait a bit, then trigger second chorus
chorus_start.beat = now() + 32
print(f"Second chorus scheduled at beat {Clock.now() + 32}")

# And a third time later in the song on a beat multiple of 64
chorus_start.beat = mod(64)
print(f"Third chorus scheduled at beat {Clock.mod(64)}")

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
