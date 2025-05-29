# Ambient Pad Exploration
# A gentle, evolving ambient soundscape with slow chord progressions

# Set a slow tempo
Clock.bpm = 70

# Start with a simple scale in C minor
Scale.default = Scale.minor
Root.default = 0

# Create an ambient pad with slow chord progression
p1 >> glass(
    [(0,2,4), (0,3,5), (-1,2,5), (-3,0,2)], 
    dur=8, 
    sus=12, 
    room=0.8, 
    mix=0.6, 
    amp=0.7,
    pan=linvar([-0.7, 0.7], 16)
)

# Add a gentle bass movement
p2 >> sawbass(
    [-7, -7, -5, -8], 
    dur=2, 
    sus=1.5, 
    lpf=800, 
    amp=0.5
)

# Subtle high bell tones
p3 >> bell(
    [7, 9, 11, 12], 
    dur=PDur(3,8)*2,
    amp=0.3,
    room=0.7,
    pan=[-0.5, 0.5]
)

# Very quiet textural element that fades in and out
p4 >> klank(
    [4, 4, 4, 5, 2, 4, 5, 4], 
    dur=0.5,
    amp=linvar([0.1, 0.3], 32),
    room=0.9,
    lpf=1500
)

# Occasional sparse percussive elements
d1 >> play(
    "..........([--]).....", 
    amp=0.4, 
    sample=2, 
    room=0.6
)

# Ambient music typically evolves slowly over time
# Let's add a slow-changing root note
def change_root():
    Root.default = var([0, -2, -5, 2], [32, 32, 32, 32])

# Uncomment to activate the root change pattern
# change_root()

# Uncomment for a slow fade out
# Master().fadeout(dur=16)