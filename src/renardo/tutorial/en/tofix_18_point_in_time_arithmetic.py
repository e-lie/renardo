# Basic arithmetic with defined PointInTime objects
po1 = PointInTime(8)
po2 = PointInTime(4)

# Operations with numbers
result1 = po1 + 4    # PointInTime(beat=12)
result2 = po1 - 2    # PointInTime(beat=6)  
result3 = po1 * 2    # PointInTime(beat=16)
result4 = po1 / 2    # PointInTime(beat=4.0)

# Operations with other PointInTime objects
result5 = po1 + po2  # PointInTime(beat=12)
result6 = po1 - po2  # PointInTime(beat=4)

print(f"po1 + 4 = {result1}")
print(f"po1 + po2 = {result5}")

# Arithmetic with undefined PointInTime objects
po_undefined = PointInTime()  # No beat set yet

# Operations are queued until beat is defined
future_point = po_undefined + 8
complex_point = (po_undefined + 4) * 2 - 1

print(f"Before defining: {future_point}")
print(f"Complex operation: {complex_point}")

# Define the base point - operations are applied automatically
po_undefined.beat = Clock.now() + 16

# The queued operations were applied to po_undefined itself
# For the derived points, we need to set their beat to trigger operations
future_point.beat = Clock.now() + 8     # (8 + 8) = 16
complex_point.beat = Clock.now() + 12   # (12 + 4) * 2 - 1 = 31

# Schedule functions using arithmetic results
def play_bass():
    b1 >> bass([0, 2, 3, 1], dur=1/2)

def play_melody():
    p1 >> pluck([4, 6, 7, 4], dur=1/4)

def play_drums():
    d1 >> play("X-o-", dur=1)

# Schedule at different calculated times
Clock.schedule(play_bass, future_point)        # At beat 16
Clock.schedule(play_melody, complex_point)     # At beat 31  
Clock.schedule(play_drums, po1 + po2 + 4)     # At beat 16 (immediate calculation)

# More complex scheduling scenarios
base_time = PointInTime()

# Chain multiple events with arithmetic
event1_time = base_time + 0      # Same as base_time
event2_time = base_time + 4      # 4 beats later
event3_time = base_time * 2      # Double the base time
event4_time = (base_time + 8) / 2 # Half of (base_time + 8)

def event1():
    print(f"Event 1 at beat {Clock.now()}")

def event2():  
    print(f"Event 2 at beat {Clock.now()}")

def event3():
    print(f"Event 3 at beat {Clock.now()}")

def event4():
    print(f"Event 4 at beat {Clock.now()}")

# Schedule all events
Clock.schedule(event1, event1_time)
Clock.schedule(event2, event2_time) 
Clock.schedule(event3, event3_time)
Clock.schedule(event4, event4_time)

# Now trigger all events by setting the base time
base_time.beat = Clock.now() + 32

print("All events scheduled with arithmetic-based timing!")

# Reverse operations also work
reverse_point = 100 - PointInTime(20)  # PointInTime(beat=80)
Clock.schedule(lambda: print("Reverse operation executed!"), reverse_point)