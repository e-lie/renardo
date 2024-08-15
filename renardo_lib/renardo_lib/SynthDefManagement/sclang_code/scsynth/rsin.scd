SynthDef.new(\rsin, {
	|bus=0, amp=1, gate=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, blur=1, beat_dur=0.5, atk=0.01, decay=0.01, rel=0.01, peak=0.9, level=0.7|
	var osc, env, osc1, osc2;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
    osc1 = VarSaw;
	env = EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sqr), doneAction: 0);
	osc = FreeVerb2.ar(*XFade2.ar(SinOscFB.ar([60,4],osc1.kr(rate)+1/2),SinOscFB.ar([freq*2,freq],526/2),osc1.kr(0.1)));
	osc = Mix(osc);
	osc = BLowShelf.ar(osc,80,2.0,-24);
	osc = osc * env * 4;
	osc = LeakDC.ar(Limiter.ar(osc,1),mul:amp);
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
