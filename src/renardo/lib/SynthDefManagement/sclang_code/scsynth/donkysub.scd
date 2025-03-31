SynthDef.new(\donkysub, {
	|vib=4, bus=0, slide=0, rate=1, atk=0.08, sus=1, rel=0.9, slidefrom=1, fmod=0, amp=1, freq=0, bits=0, pan=0, frate=2|
	var osc, env;
	freq = freq + fmod;
	freq = Line.ar(freq * slidefrom, freq * (1 + slide), sus);
	freq = Vibrato.kr(freq, rate: vib);
	amp = (amp * 6);
	freq = (freq / (frate + 0.1));
	osc = Ringz.ar(Impulse.ar(0), [freq, (freq + 2)], sus, amp);
	env = EnvGen.ar(Env.asr(atk, sus, rel, curve: \sin), doneAction:0);
	osc = osc * env * amp * 0.1;
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \bass,
	tags: [\tag]
	)
).add;
