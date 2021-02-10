SynthDef.new(\acidbass, {
	arg bus = 0, gate = 1, freq = 440, amp = 1, pan = 0, fmod=0, atk = 0.001, dec = 0.4, sus = 1, rel = 0.3, curve = -4, lagTime = 0.12, filterRange = 6, width = 0.51, rq = 0.4;
	var ampEnv, filterEnv, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = Lag.kr(freq, lagTime);
	ampEnv = Env.adsr(
		attackTime: atk,
		decayTime: dec,
		sustainLevel: sus / 20,
		releaseTime: rel,
		peakLevel: amp * 0.3,
		curve: [0, curve, curve, curve]
	).kr(gate: gate, doneAction: 0);
	filterEnv = Env.adsr(
		attackTime: atk,
		decayTime: dec * 2,
		sustainLevel: sus * 1/20,
		releaseTime: rel,
		peakLevel: 2.pow(filterRange), // octaves multiplier
		curve: [-1 * curve, curve],
		bias: 1 // env sweeps from 1 to 2.pow(filterRange) and back
	).kr(gate: gate, doneAction: 0);
	osc = LFPulse.ar(freq: freq, width: width).range(-1, 1);
	osc = RLPF.ar(osc, freq * filterEnv, rq);
	osc = osc * ampEnv;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "otophilia",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	description: "",
	category: \bass,
	tags: [\pitched, \acid, \phat, \subtractive]
	)
).add;