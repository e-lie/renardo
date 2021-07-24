SynthDef.new(\tworgan4, {
	//Standard Values
	|bus=0, pan=0, freq=440, amp=1, gate=1, fmod=0, atk=0.1, sus=1, rel=0.3,
	//Other controls (blend goes from 0 to 1)
	lforate=4.85, lfodepth=0.006, cutoff=5000, rq=0.5, parfreq=400, parrq=1, pardb=3, blend=0.6|
	var lfo, pulse, filter, fenv, env, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	amp = amp / 2;
	lfo = LFTri.kr(freq: lforate * [1, 1.01], iphase: Rand(0, 2.0) ! 2).range(1 / (1 + lfodepth), (1 + lfodepth));
	pulse = Pulse.ar(freq: freq * [1, 3] * lfo, width: [0.5, 0.51], mul: [(1 - blend), blend]);
	env = Env.linen(atk, sus, rel, curve:\sin).kr(doneAction: 0);
	filter = BLowPass4.ar(in: pulse, freq: cutoff, rq: rq);
	filter = BPeakEQ.ar(in: filter, freq: parfreq, rq: parrq, db: pardb);
	osc = Mix.ar([filter]);
	osc = osc * env * amp * 0.15;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Nick Collins",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	description: "Subtractive tonewheel organ from Steal this Sound example",
	category: \organ,
	tags: [\pitched]
	)
).add;