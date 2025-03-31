SynthDef.new(\dust, {
	|amp=1, sus=1, pan=0, freq=440, vib=0, fmod=0, rate=1, bus=0|
	var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq + fmod];
	osc = Dust.ar(freq + rate);
	env = EnvGen.ar(Env.new([1, 1], [1, 1]), doneAction: 0);
	osc = (osc * env * amp);
	osc = Mix(osc) * 0.25;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "CrashServer",
	modified_by: "Modifier",
	decription: "Dust noise via random impulses",
	category: \noise,
	tags: [\tag, \tag]
)).add;