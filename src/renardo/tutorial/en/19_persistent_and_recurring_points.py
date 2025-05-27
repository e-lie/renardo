# Basic PointInTime recap

# Regular PointInTime can only be used once
drop_moment = PointInTime()

# {drop_moment}
p1 >> saw([0], amp=2)
d1 >> play("X---", amp=2)

drop_moment.beat = Clock.now() + 8
# After this triggers, drop_moment is "used up" and can't be triggered again


# === PERSISTENT POINT IN TIME ===

# Create a persistent point for chorus sections
chorus_start = PersistentPointInTime()

print(f"Created chorus trigger: {chorus_start}")

# Schedule what happens during chorus
# {chorus_start}
p1 >> pluck([0, 2, 4, 2], dur=1/2, amp=0.8).stop(2)
b1 >> bass([0, 0, 2, 2], dur=2, amp=0.6).stop(2)
d1 >> play("X-o-X-o-", dur=1/2).stop(2)

# Now you can trigger the chorus multiple times!

# First chorus at beat 16
chorus_start.beat = Clock.now() + 16
print(f"First chorus scheduled at beat {Clock.now() + 16}")
print(f"Chorus state after trigger: {chorus_start}")  # Should be undefined again

# Wait a bit, then trigger second chorus
chorus_start.beat = Clock.now() + 32
print(f"Second chorus scheduled at beat {Clock.now() + 32}")

# And a third time later in the song
chorus_start.beat = Clock.now() + 64
print(f"Third chorus scheduled at beat {Clock.now() + 64}")

# Each trigger executes the same musical pattern!

# === RECURRING POINT IN TIME ===

# Create a recurring point for hi-hat patterns every 4 beats
hihat_pattern = RecurringPointInTime(period=16)
print(f"Created recurring hi-hat trigger: {hihat_pattern}")

# Schedule the hi-hat pattern
# {hihat_pattern}
hh >> play("--[--]-", dur=1/4, amp=0.4).stop(2)

# Start the recurring pattern
hihat_pattern.beat = Clock.now() + 4
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

# === ARITHMETIC OPERATIONS ===

# Both types support full arithmetic operations
verse_trigger = PersistentPointInTime()
bridge_pattern = RecurringPointInTime(period=8)

# Arithmetic with persistent points
melody_entry = verse_trigger + 2
harmony_entry = verse_trigger + 4

print(f"verse_trigger + 2 = {melody_entry}")
print(f"verse_trigger + 4 = {harmony_entry}")

# {melody_entry}
p3 >> pluck([4, 6, 7, 4], dur=1/2)

# {harmony_entry}
p4 >> pluck([7, 9, 11, 7], dur=1/2, oct=5)

# Arithmetic with recurring points
bridge_buildup = bridge_pattern - 1
bridge_breakdown = bridge_pattern + 4

print(f"bridge_pattern - 1 = {bridge_buildup}")
print(f"bridge_pattern + 4 = {bridge_breakdown}")

# {bridge_buildup}
# Tension building 1 beat before each bridge
fx1 >> play("~", fx=reverb(0.8))

# {bridge_breakdown}
# Breakdown 4 beats into each bridge
p1.stop()
d1 >> play("X---X---", amp=0.8)

# === COMPLEX SCHEDULING SCENARIOS ===

# Song structure with multiple persistent points
intro_point = PersistentPointInTime()
verse_point = PersistentPointInTime() 
chorus_point = PersistentPointInTime()
outro_point = PersistentPointInTime()

# Recurring elements that run throughout
steady_kick = RecurringPointInTime(period=1)  # Every beat
snare_hits = RecurringPointInTime(period=2)   # Every 2 beats
cymbal_crash = RecurringPointInTime(period=8) # Every 8 beats

# {steady_kick}
k1 >> play("X", amp=0.7)

# {snare_hits + 1}  # Offset snare by 1 beat
s1 >> play("o", amp=0.6)

# {cymbal_crash}
c1 >> play("*", amp=0.5)

# Song arrangement

# Intro
# {intro_point}
p1 >> pluck([0, 2, 4, 2], dur=2, amp=0.3)
print("Intro section playing...")

# {intro_point + 8}  # Intro builds after 8 beats
p1 >> pluck([0, 2, 4, 2], dur=1, amp=0.5)

# Verse sections
# {verse_point}
p1 >> pluck([0, 2, 4, 7, 4, 2], dur=1/2, amp=0.6)
b1 >> bass([0, 0, 2, 2], dur=2, amp=0.5)
print("Verse section playing...")

# Chorus sections (more energetic)
# {chorus_point}
p1 >> saw([0, 4, 7, 4], dur=1/2, amp=0.8, lpf=2000)
b1 >> bass([0, 2, 0, 2], dur=1, amp=0.7)
d1 >> play("X-o-X-o-", dur=1/2, amp=0.8)
print("Chorus section playing...")

# Outro (fade out)
# {outro_point}
p1 >> pluck([0, 2, 4, 2], dur=2, amp=0.3)
b1.stop()
d1.stop()
print("Outro section playing...")


# === PERFORMANCE TIPS ===
print("\n=== Performance Tips ===")

# Start recurring patterns early
kick_pattern = RecurringPointInTime(period=1)
# {kick_pattern}
# k >> play("X", amp=0.8)

# Start immediately to establish rhythm
kick_pattern.beat = Clock.now()
print("Tip: Start recurring rhythmic patterns immediately with Clock.now()")

# Use persistent points for song sections
section_a = PersistentPointInTime()
section_b = PersistentPointInTime()

# Pre-define your sections
# {section_a}
# # Calm section
# p1 >> pluck([0, 2, 4], dur=1, amp=0.5)

# {section_b}
# # Energetic section  
# p1 >> saw([0, 4, 7], dur=1/2, amp=0.8)

print("Tip: Pre-define song sections, trigger them live during performance")

# Stop recurring patterns when needed
# To stop a recurring pattern, you need to clear its schedulables
print("Tip: To stop recurring patterns, use Player.stop() methods for the instruments")

# Combine with TimeVar for evolving patterns
evolving_pattern = RecurringPointInTime(period=4)

# {evolving_pattern}
# p1 >> pluck(var([[0, 2], [4, 7], [0, 4, 7]], 8), dur=1/2)

print("Tip: Combine with TimeVar for patterns that evolve over time")

