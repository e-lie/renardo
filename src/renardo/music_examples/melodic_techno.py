b2 >> blip(
    [0, -1, 2, 5, [2, 2.5], -1],
    dur=0.5,
    sus=linvar([0.3, 1, 4, 1], 8),
    oct=P[6, 4, 5].stutter(4),
    lpf=800,
)

b1 >> pluck(
    [0, -1, 2, 5, [2, 2.5], -1],
    dur=[0.5, 0.25, 0.25],
    sus=linvar([0.3, 1, 4, 1], 8),
    oct=P[6, 4, 5].stutter(4),
    lpf=400,
)

d1 >> play("V(.(o.).[.O])", lpf=2600).eclipse(16, 64)
hh >> play(".-", sample=3)


Clock.meter = (4, 4)
Clock.bpm = 140
