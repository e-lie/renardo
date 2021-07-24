SynthDef.new(\supersaw, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, rel=0.01, peak=1, level=0.8, phase=0, noiserate=0.5|
	var osc, env;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = {freq * LFNoise2.kr(noiserate).range(0.98, 1.02)}!20;
	amp = (amp / 20);
	osc = LFSaw.ar(freq, phase);
	env = EnvGen.ar(Env.linen(atk, sus, rel, curve: \lin), doneAction: 0);
	osc = Mix(osc);
	osc = osc * env * amp * 0.2;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "unknown",
	modified_by: "Jens Meisner",
	description: "",
	category: \pads,
	tags: [\pitched]
	)
).add;