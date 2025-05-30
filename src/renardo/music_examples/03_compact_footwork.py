
Clock.bpm=160

b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6])
k2 >> play("v.(.x)(v*)*v.", dur=.25)
d2 >> play("{cccc.}", dur=var([2, 2 / 3], [12, 4]), rate=(1.2, 2.4), lpf=800)