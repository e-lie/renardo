SynthDef.new(\ladder, {
	|amp=1, sus=1, pan=0, freq=440, vib=0, fmod=0, rate=0, bus=0|
	var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc = MoogLadder.ar(LFSaw.ar(freq),  LinExp.kr(LFCub.kr(rate, 1*pi), -1, 1, 180, 8500), 0.75);
	env = EnvGen.ar(Env.new([1, 1], [1, 1]), doneAction:1);
	// env=EnvGen.ar(Env(times: [(sus / 2), (sus / 2)],levels: [0, amp, 0],curve: 'lin'), doneAction: 0);
	osc = (osc * env * amp);
	osc = Mix(osc) * 1;
	osc = Pan2.ar(osc * amp, pan);
	ReplaceOut.ar(bus, osc)
	},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \category,
	tags: [\tag]
	)
).add;