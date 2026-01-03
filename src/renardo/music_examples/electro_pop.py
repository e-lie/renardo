Clock.bpm = 150

p1 >> pluck(
    [0, [0, _], 0, [4, 4, 3, _], 7, 3, -3, 2],
    dur=0.5,
    sus=10,
    oct=[4, [5, 4, 6], 4, [5, 6]],
    lpf=800,
    hpf=400,
) + var([0, 2, 0, 7])

hh >> play(
    "--", sample=4, dur=[0.25], rate=linvar([1, 2], [8, 0]), room2=0.5, lpf=2000
).eclipse(2, 8, 6)
h2 >> play("(...-).-(.-)", sample=3, dur=[0.22, 0.28, 0.25, 0.25], room2=0.04)

k1 >> play("(V.).(.x.)(v.)", dur=0.25, lpf=600, rate=linvar([1, 1.2, 1.2], [16, 16, 0]))

cp >> play(
    ".(.{oo.}o.)(..{oo.}.)",
    rate=PWhite(1, 1.5)[:4] / 1.5,
    sample=0,
    dur=[0.4, 0.6, 0.5, 0.5],
)
