SynthDef.new(\fbass, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.001, decay=1, rel=0.2, cutoff = 250, rq = 0.35|
	var total, exciter, osc, env, sub;
	sus = sus*blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = freq / 4;
	total = (atk + sus + decay + rel) * freq;
	exciter = Env.new(levels: [0, 1, 1, 0, 0], times: [atk, decay, sus, rel]/total).ar;
	env = EnvGen.ar(Env([0,1,0.8,0.8,0], [0.002, 0.01, sus, sus]), doneAction: 0);
	// Delay line
	osc = CombN.ar(in: exciter, maxdelaytime: 0.06, delaytime: 1/freq, decaytime: sus);
	// LPF
	osc = RLPF.ar(in: osc, freq: LinExp.ar(Amplitude.ar(in: osc), 0, 1, cutoff, 18000), rq: rq);
	// Compressor for fun
	osc = CompanderD.ar(in: osc, thresh: 0.4, slopeBelow: 1, slopeAbove: 1/2.5);
	osc = Mix.ar(osc.tanh);
	osc = LeakDC.ar(osc);
	osc = osc * env * amp;
	osc = Pan2.ar(osc, pan);
    ReplaceOut.ar(bus, osc);
},
metadata: (
	credit: "Josh Mitchell, CrashServer",
	modified_by: "",
	description: "",
	category: \bass,
	tags: [\pitched, \bass]
	)
).add;