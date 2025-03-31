SynthDef.new(\latoo, {
	|amp=1, sus=1, pan=0, freq=440, vib=0, atk=0.01, rel=0.9, fmod=0, rate=0, bus=0|
	var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc = Latoocarfian2DN.ar(SampleRate.ir / 4, SampleRate.ir, LFNoise2.kr(2.dup, 1, 1), d: LFNoise2.kr(2.dup, 0.5, 1),  mul:0.2);
	env = EnvGen.ar(Env.asr(atk, sus, rel, curve: \lin), doneAction: 0);
	osc = (osc * env * amp);
	osc = Mix(osc) * 0.5;
	osc = Pan2.ar(osc * amp, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \ambient,
	tags: [\tag]
	)
).add;