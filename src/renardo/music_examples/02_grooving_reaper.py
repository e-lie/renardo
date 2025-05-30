Clock.bpm=100

k1 >> play("V.X(...V)", lpf=1500, dur=[.5,.47,.53,.5], rate=1.2).eclipse(16,128,128-16)

cc >> play("c{c.}", dur=[1/3,2/3], rate=12)

sn >> play(".(o[.o]o(oo[o.o(.o)]o))", sample=1, amp=[1.2,.8], rate=linvar([1,1.5],32))

hh >> play("-", sample=1, dur=.25, amp=P[1,.3,.5,.8]*1.3, rate=linvar([1,1.5],32)).eclipse(8,32,16)

Root.default = var([0,0,5,4,0,2,0,2],4)

b3 >> pluck([[1,_,2],0,[_,2],2], dur=P[.25,.5,.25,.25], sus=[1,.25,.5,.75], oct=[4,5,6], amp=.7, lpf=linvar([600,2000],32))

# Reaper instruments (see reaper tutorial)
b1 >> pluckbass([0,0,2], dur=[.72,.78,.5], oct=3, buzz=linvar([.2,.6], 16), drive=.5)

b2 >> lonesine([[_,0,2],0,[0,_],2], dur=P[.25,.5,.25,.25], oct=[4,5,6], amp=.5)