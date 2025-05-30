Root.default = var([0,2,4], [2,4,6])
d1 >> play("<x-{-[--]}><*....><..(ooo(oO)).>")
d2 >> blip([2,_,[4,4,4,P*(5,2)],_], dur=.5, sus=linvar([.2,.5,3],16), pan=[-.8,0,.8]).eclipse(4,16)
d3 >> pluck(dur=.25, oct=3, sus=linvar([.2,.5,3],16), amp=[.7,.7,1,2], lpf=linvar([400,600,3000],16)).eclipse(16,96)
k2 >> play("V.", lpf=400).eclipse(64,128)

d2.dur=var([.25,1/3,1/2], 16)

Master().fadeout(dur=24)
