# Minimal Techno Groove
# A driving techno beat with acid bass and atmospheric elements

# Set a typical techno tempo
Clock.bpm = 126

# Set scale to minor
Scale.default = Scale.minor
Root.default = 0

# Main kick and percussion patterns
d1 >> play("x---x---x---x-o-", sample=1, lpf=600, dur=1/4, amp=0.8)
d2 >> play("----o-------o---", sample=3, room=0.3, dur=1/4, amp=0.5)
d3 >> play("------s-s-s-s---", sample=2, pan=[-0.5, 0.5], dur=1/4, amp=0.4)

# Acid-style bassline with some variation
b1 >> sawbass(
    [0, 0, 0, 0, 3, 3, 3, 3, 5, 5, 7, 7, 8, 7, 5, 3],
    dur=1/4,
    sus=1/8,
    lpf=linvar([500, 2000], 16),
    resonance=0.3,
    amp=0.6
)

# Add a rhythmic synth pattern
p1 >> pulse(
    [0, 5, 7, 9], 
    oct=4, 
    dist=0.03,
    dur=PDur(3,8)/2,
    pan=0.2,
    amp=0.4
)

# Occasional atmospheric pad
p2 >> glass(
    [0, 2, 4], 
    dur=8, 
    sus=12, 
    chop=16, 
    room=0.8, 
    mix=0.5,
    amp=0.3
)

# Add variation using linvar for filter cutoff
p2.lpf = linvar([400, 3000], 32)

# Uncomment to create a minimal breakdown section
# def breakdown():
#     d1 >> play("x---x---x---x-o-", sample=1, lpf=600, dur=1/4, amp=[0.8, 0, 0, 0])
#     p2.amp = 0.5
# 
# breakdown()