SynthDef.new(\tremsynth, {
	|bus=0, freq=0, amp=1, pan=0, fmod=0, atk=0.01, sus=1, rel=0.1, pos=0, modfreq=3|
	var osc, mod, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	mod = SinOsc.kr(freq: modfreq, mul: 1).range(0,1);
	osc = LFTri.ar(freq: freq, mul: mod);
	env = Env.linen(atk, sus, rel, curve: \lin).kr(doneAction: 0);
	osc = Mix(osc);
	osc = osc * env * amp * 0.15;
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
