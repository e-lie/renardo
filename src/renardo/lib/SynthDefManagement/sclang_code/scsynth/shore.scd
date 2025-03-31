SynthDef.new(\shore, {
	|bus=0, dur=1, amp=1, fmod=0, freq=0, pan=0, noiselevel=0.1, density=100|
	var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = EnvGate.new(doneAction: 0, curve: \sin);
	osc = OnePole.ar(WhiteNoise.ar(noiselevel) + Dust.ar(density, 0.5), 0.7);
	osc = osc + Splay.ar(FreqShift.ar(osc, 1/(4..9)));
	osc = osc * env * amp;
	osc = Mix(osc) * 0.1;
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