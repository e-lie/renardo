SynthDef.new(\tritri, {
	|amp=1, sus=1, gate=1, pan=0, modfreq=5 freq=0, vib=0, fmod=0, rate=4.85, phase=0.5, cutoff=2000, rq=0.5, mul=1, bus=0, atk=0.0001, decay=0.01, rel=0.01, level=0.8, peak=1|
	var osc, pulse, filter,env, modulator;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	modulator = SinOsc.ar(modfreq).range(0, 1);
	osc  = LFTri.ar(freq: freq, mul: modulator);
	env = EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
	osc = BLowPass4.ar(osc,(cutoff*(env.squared))+200+freq,rq);
	osc = Mix(osc*env) * amp * 0.3;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "CrashServer",
	modified_by: "",
	description: "",
	category: \organ,
	tags: [\tag]
	)
).add;