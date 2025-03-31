SynthDef.new(\dustv, {
	|amp=1, sus=1, pan=0, freq=440, vib=0, atk=0.01, rel=0.09, fmod=0, reverbtime=3, roomdepth=8, rate=0, room=0, bus=0|
	var osc, env, random;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	random = Dwhite(0.0, 1.0, inf);
	osc = GVerb.ar(CombC.ar(Dust.ar(rate+5) / Blip.ar(freq, Line.kr(5, 120, 200), 0.2), Dust.ar(random), 0.01, 0.02), roomdepth, reverbtime, mul: 0.001);
	//env = EnvGen.ar(Env.new([1, 1], [1, 1]), doneAction: 0);
	env = EnvGen.ar(Env.linen(atk, sus, rel, curve:\lin), doneAction: 0);
	osc = (osc * env * amp);
	osc = Mix(osc) * 0.3;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \noise,
	tags: [\tag]
	)
).add;