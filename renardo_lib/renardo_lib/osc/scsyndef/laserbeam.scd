SynthDef.new(\laserbeam, {
	|bus = 0, pan = 0.0, freq = 0, amp = 1, fmod=0, atk = 0.01, sus = 1|
	var osc, freqenv, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freqenv = EnvGen.ar(Env([4, 0.5, 1, 1], [atk, 0.01, 1.0]));
	env = EnvGen.ar(Env([atk, sus, 0.0], [atk, sus, 0.1]),levelScale: amp, doneAction: 0);
	osc = LFTri.ar(freq: freq * freqenv);
	osc = osc * env * amp * 0.2;
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Mitchell Sigman",
	modified_by: "Jens Meisner",
	description: "",
	category: \keys,
	tags: [\synthesizer, \misc]
)).add;


