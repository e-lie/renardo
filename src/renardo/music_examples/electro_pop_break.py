ableton_instruments = create_ableton_instruments(max_midi_tracks=16, scan_audio_tracks=True)

syntheee = ableton_instruments["syntheee"].out
nevere = ableton_instruments["nevere"].out

Clock.bpm = 140

Scale.default = Scale.major

Clock.midi_nudge=-.06

d2 >> nevere([0,1,5], dur=16)

p1 >> blip(
    [0, [0, _], 0, [4, 4, 3, _], 7, 3, -3, 2],
    dur=.5,
    sus=10,
    oct=[4, [5, 4, 6], 4, [5, 6]],
    lpf=800,
    hpf=400,
    amp=.3,
) + var([0, 2, 0, 7])
p1.fadein(128)
d1 >> syntheee()

p1.eclipse(16,64)

Scale.default = Scale.minor

hh >> play(
    "--", sample=4, dur=[0.25], rate=linvar([1, 2], [8, 0]), room2=linvar([.2,0,1],[32,32,0]), lpf=2000
).eclipse(2, 8, 6).eclipse(1,64,63)

h2 >> play("(....).-(.-)", sample=3, dur=[0.22, 0.28, 0.25, 0.25], room2=linvar([.05,0,1],[32,32,0])).eclipse(1,64,63)

k1 >> play("(V.).(...)(..)", dur=0.25, lpf=600, rate=linvar([1, 1.2, 1.2], [16, 16, 0]), hpf=80, sample=var([0,2],64)).eclipse(4,64,60)

h2 >> play("(...-).-(.-)", sample=3, dur=[0.22, 0.28, 0.25, 0.25], room2=linvar([.05,0,1],[32,32,0])).eclipse(1,64,63)

k1 >> play("(V.).(.x.)(..)", dur=0.25, lpf=600, rate=linvar([1, 1.2, 1.2], [16, 16, 0]), hpf=80, sample=var([0,2],64)).eclipse(4,64,60)

Root.default = var([0,0,5,7], [16,16,8,8])

k1 >> play("(V.).(.x.)(v.)", dur=0.25, lpf=600, rate=linvar([1, 1.2, 1.2], [16, 16, 0]), hpf=80, sample=var([0,2],64)).eclipse(4,64,60)

k1 >> play("<..x..><x..><V...>", dur=0.25, lpf=600, rate=linvar([1, 1.2, 1.2], [16, 16, 0]), hpf=80, sample=var([1,2],64)).eclipse(4,64,60)

k2 >> play("{xxxx.}", dur=.25, amp=linvar([0,0,2],[32,32,0]), rate=linvar([1,1,2],[32,32,0])*.5, lpf=800, room2=linvar([0,0,.5],[32,32,0])).eclipse(4,64,60)

cp >> play(
    "-{.--[--]}-.",
    rate=PWhite(1, 1.5, seed=3)[:16] / 1.5,
    sample=0,
    dur=[0.4, 0.6, 0.5, 0.5],
).eclipse(4,64,60)