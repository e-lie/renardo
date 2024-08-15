SynthDef.new(\rissetobell, {
	|bus = 0, pan = 0, freq = 440, amp = 0.1, fmod = 0, atk = 0.1, sus=1, rel = 0.9, gate = 1|
	var amps, durs, frqs, dets, doneActionEnv, env, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = freq * 2;
	amps = #[1, 0.67, 1, 1.8, 2.67, 1.67, 1.46, 1.33, 1.33, 1, 1.33];
	durs = #[1, 0.9, 0.65, 0.55, 0.325, 0.35, 0.25, 0.2, 0.15, 0.1, 0.075];
	frqs = #[0.56, 0.56, 0.92, 0.92, 1.19, 1.7, 2, 2.74, 3, 3.76, 4.07];
	dets = #[0, 1, 0, 1.7, 0, 0, 0, 0, 0, 0, 0];
	doneActionEnv = Env.linen(atk, sus, rel, curve: \sin).ar(gate: gate, doneAction: 0);
	osc = Mix.fill(11, {arg i; env = Env.perc(attackTime: atk, releaseTime: sus + rel * durs[i], level: amps[i],
		curve: atk.explin(0.005, 4, -4.5, 0)).ar(gate: gate); SinOsc.ar(freq: freq * frqs[i] + dets[i], mul: env * amp);
	});
	osc = osc * doneActionEnv * amp * 0.05;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Jean-Claude Risset's bell",
	modified_by: "Jens Meisner",
	description: "",
	category: \bells,
	tags: [\percussion, \bell, \inharmonic]
)).add;
