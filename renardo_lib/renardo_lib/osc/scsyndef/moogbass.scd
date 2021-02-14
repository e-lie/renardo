SynthDef.new(\moogbass, {
	|bus = 0, pan = 0, freq = 440, amp = 1, fmod=0, gate = 1, cutoff = 1200, gain = 1.2, lagamount = 0.01, atk = 0.1, dec = 0.4, sus = 1, rel = 0.3|
	var filter, env, filterenv, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc = Mix(VarSaw.ar(freq: freq.lag(lagamount) * [1.0, 1.001, 2.0], iphase: Rand(0.0,1.0)!3, width: Rand(0.5,0.75)!3, mul: 0.4));
	filterenv = EnvGen.ar(envelope: Env.asr(atk, sus, rel), gate: gate);
	filter =  MoogFF.ar(in: osc, freq: cutoff * (1.0 + (0.8 * filterenv)), gain: gain);
	env = EnvGen.ar(envelope: Env.adsr(atk, 1.2, sus, rel, amp), gate: gate, doneAction: 0);
	osc = (0.9 * filter + (0.3 * filter.distort));
	osc = osc * env * amp * 0.3;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Nick Collins",
	modified_by: "Bruno Ruviaro, Jens Meisner",
	description: "",
	category: \bass,
	tags: [\pitched, \bass]
)
).add;