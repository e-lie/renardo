# Basic PointInTime recap

# Regular PointInTime can only be used once
drop_moment = pit()
b1 >> blip()

# {drop_moment}
p1 >> saw([0], amp=2)
d1 >> play("X---", amp=2)

drop_moment.beat = Clock.now() + 8
# After this triggers, drop_moment is "used up" and can't be triggered again


# === PERSISTENT POINT IN TIME ===

# Create a persistent point for chorus sections
chorus_start = ppit() # or PersistentPointInTime()
p2 >> pluck([0,2,2,5],oct=4)
print(f"Created chorus trigger: {chorus_start}")

# Schedule what happens during chorus
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

# Each trigger executes the same musical pattern!

# === RECURRING POINT IN TIME ===

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


# === CLEANING AND CANCELING SCHEDULED EVENTS ===

# All PointInTime classes have a clean() method to remove scheduled operations
cleanup_point = pit()

def some_function():
    print("This function was scheduled")

# Schedule something
Clock.schedule(some_function, cleanup_point)
print(f"Function scheduled: {cleanup_point}")

# Change your mind and cancel everything
cleanup_point.clean()
print(f"After clean(): {cleanup_point}")

# Now even if you set the beat, nothing will happen
cleanup_point.beat = Clock.now() + 8
print("Beat set but nothing executes (was cleaned)")

print("--- Practical Cleaning Examples ---")

# Stop a recurring pattern
drum_pattern_to_stop = rpit(period=4)

# {drum_pattern_to_stop}
d4 >> play("X-o-", dur=1/2)

# Start the pattern
drum_pattern_to_stop.beat = Clock.now() + 4

# Later, stop it completely
drum_pattern_to_stop.clean()
print("Drum pattern stopped with clean()")

# Reset a persistent trigger for new content
verse_trigger_reset = ppit()

# {verse_trigger_reset}
p5 >> pluck([0, 2, 4], dur=1)

# Later, completely change what the verse does
verse_trigger_reset.clean()

# {verse_trigger_reset}  # Now schedule something completely different
p5 >> saw([0, 4, 7], dur=1/2, lpf=1000)

print("Verse trigger reset for new content")

print("✓ clean() method provides powerful control over scheduled events!")

print("Summary:")
print("✓ PointInTime: Single-use scheduling")
print("✓ PersistentPointInTime: Reusable triggers for song sections") 
print("✓ RecurringPointInTime: Automatic periodic execution")
print("✓ All support arithmetic operations with type preservation")
print("✓ All have clean() method for canceling/resetting scheduled events")
print("✓ Perfect for live coding performances and complex arrangements")
