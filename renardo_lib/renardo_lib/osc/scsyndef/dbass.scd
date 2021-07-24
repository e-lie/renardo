SynthDef.new(\dbass, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=1, bus=0|
	var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod] * Line.ar(Rand(0.5, 1.5), 1, 0.02);
	freq = (freq / 4);
	osc = ( VarSaw.ar(freq, width: LFTri.ar((0.5 * rate) / sus, iphase:0.9, add:0.8, mul: 0.2), mul: amp * 0.08));
	env = EnvGen.ar(Env([0, 1, 0.8, 0.8, 0], [0.02, 0.01, sus/2, sus/2]), doneAction: 0);
	osc = Mix(osc * env);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
