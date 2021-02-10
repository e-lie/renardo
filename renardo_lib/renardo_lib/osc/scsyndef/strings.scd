SynthDef.new(\strings, {
	//Standard Definitions
	|bus = 0, freq = 440, amp = 1, gate = 1, pan = 0, fmod=0, freqLag = 0.9, atk = 0.1, sus = 1, rel = 0.2,
	//Other Controls (mix ranges from 0 - 1)
	rq = 0.012, combHarmonic = 4, sawHarmonic = 1.5, mix = 0.33|
	var env, osc, combFreq;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	combFreq = 1 / (Lag.kr(in: freq, lagTime: freqLag / 2) * combHarmonic);
	env = Env.linen(atk, sus, rel, curve: \sin).kr(gate: gate, doneAction: 0);
	osc = SyncSaw.ar(syncFreq: freq * WhiteNoise.kr().range(1/1.025, 1.025), sawFreq: freq * sawHarmonic, mul: 8);
	osc = (osc * (1 - mix)) + PinkNoise.ar(180 * mix);
	osc = CombL.ar(osc, combFreq, combFreq, -1); //Try positive 1 for decay time as well.
	osc = Resonz.ar(osc, Lag.kr(in: freq, lagTime: freqLag), rq).abs;
	osc = Limiter.ar(osc, amp * 1/3);
	osc = Mix.ar(osc * env * amp);
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