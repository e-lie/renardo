SynthDef.new(\strings, {
	//Standard Definitions
	|bus = 0, freq = 440, amp = 1, gate = 1, pan = 0, fmod=0, atk = 0.1, sus = 1, rel = 0.2,
	//Other Controls (mix ranges from 0 - 1)
	freqlag = 0.9, rq = 0.012, combharm = 4, sawharm = 1.5, mix = 0.33|
	var env, osc, combFreq;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	combFreq = 1 / (Lag.kr(in: freq, lagTime: freqlag / 2) * combharm);
	env = Env.linen(atk, sus, rel, curve: \sin).kr(gate: gate, doneAction: 0);
	osc = SyncSaw.ar(syncFreq: freq * WhiteNoise.kr().range(1/1.025, 1.025), sawFreq: freq * sawharm, mul: 8);
	osc = (osc * (1 - mix)) + PinkNoise.ar(180 * mix);
	osc = CombL.ar(osc, combFreq, combFreq, -1); //Try positive 1 for decay time as well.
	osc = Resonz.ar(osc, Lag.kr(in: freq, lagTime: freqlag), rq).abs;
	osc = Mix.ar(osc) * env * amp;
	osc = Limiter.ar(osc, amp * 0.1);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Original from Julian Rohrhuber, 2007",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	description: "",
	category: \strings,
	tags: [\pitched]
	)
).add;