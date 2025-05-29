# Hip-Hop Beat
# A classic boom-bap style hip-hop beat with samples and bass

# Set a hip-hop tempo
Clock.bpm = 90

# Set scale to minor pentatonic
Scale.default = Scale.penta
Root.default = 0

# Main drum pattern
d1 >> play("x.x.x...", sample=0, amp=0.9, lpf=1200)     # Kick
d2 >> play("..o...o.", sample=2, amp=0.7, room=0.1)     # Snare
d3 >> play("------s-s---s---", sample=3, amp=0.4)       # Hi-hat
d4 >> play("--------c-------", sample=2, amp=0.5)       # Crash

# Bass line
b1 >> sawbass(
    [0, 0, 0, 0, 3, 2, 0, -2],
    amp=0.6,
    lpf=500,
    dur=1/2,
    sus=0.4,
    oct=5
)

# Sample chopping (using built-in samples)
a1 >> loop(
    "loop", 
    P[0:8], 
    dur=1, 
    amp=0.6, 
    lpf=2000, 
    formant=var([0,1,2], 16)
)

# Melodic elements
p1 >> piano(
    [0, 2, 3, 7, 8, 7, 3, 2], 
    dur=[1/2, 1/2, 1, 1/2, 1/2, 1/2, 1/2, 1], 
    amp=0.4, 
    oct=6, 
    room=0.5
)

# Variation for 2nd part
def alternate_section():
    d2 >> play("..o...o.", sample=1, amp=0.7, room=0.3)
    b1 >> sawbass(
        [0, 0, 3, 2, 5, 3, 2, 0],
        amp=0.6,
        lpf=800,
        dur=1/2,
        sus=0.3
    )
    p1 >> piano(
        [2, 3, 5, 7, 8, 7, 5, 3], 
        dur=1/2, 
        amp=0.4, 
        oct=6, 
        room=0.5
    )

# To switch sections, uncomment:
# alternate_section()