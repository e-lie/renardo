SynthDef.new(\garfield, {
	|bus=0, freq=440, amp=1, pan=0, gate=1, fmod=0, atk=0.01, sus=1, phase=0, smooth=0.5, mult=3, vibrato=1, rq=1|
	var env, osc, del;
	freq = In.kr(bus,1);
	freq = [freq, freq+fmod];
	env = Env.linen(atk, sus, 0.1, curve:\sin).kr(doneAction:0);
	del = SinOsc.ar(1/8, phase, mult);
	osc = SinOscFB.ar(freq, 0.3, add: SinOsc.ar(vibrato));
	osc = CrossoverDistortion.ar(osc, 0.8, smooth);
	osc = RLPF.ar(osc, 2800, rq) + osc;
	osc = CombN.ar(osc, 0.03, 0.085);
	osc = Splay.ar(osc);
	osc = Mix(osc);
	osc = LeakDC.ar(Limiter.ar(osc * 0.08, 1));
	osc = osc * env * amp * 0.2;
	osc = osc.tanh;
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc);
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
