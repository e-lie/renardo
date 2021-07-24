SynthDef.new(\combs, {
	//Standard Arguments
	|bus=0, pan=0, amp=1, freq=440, gate=1, fmod=0, atk=0.01, sus=1, rel=0.3,
	//Other Controls
	vibrate=2, depth=0.8, regen= -3, sweep=8, rq=0.9, nharm=2|
	var max, min, vibrato, osc, env, filterenv;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	//Setting some values for the filters:
	min = ((1 + depth) / freq);
	max = (1 / (freq * (1 + depth)));
	vibrato = LFNoise1.ar(vibrate).range(min, max);
	//Amplitude and filter cutoff envelopes
	env = Env.asr(atk, sus, rel, curve: \sin).kr(gate: gate, doneAction: 0);
	filterenv = Env.perc(atk, sus + rel).kr;
	filterenv = ((filterenv * sweep) + 1) * freq;
	//The core noise:
	osc = Mix.ar([BrownNoise.ar(1) * 1/4, freq]);
	osc = CombL.ar(osc, max, vibrato, regen);
	osc = CombN.ar(osc, nharm / freq, nharm / freq, regen, env);
	//More filters and output stuff:
	osc = RHPF.ar(osc, freq * 2, rq);
	osc = RLPF.ar(osc, filterenv, rq, amp);
	osc = Limiter.ar(osc, amp);
	osc = Mix(osc) * 0.02;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Josh Mitchell",
	modified_by: "Jens Meisner",
	description: "Modification of combs bass synth led to ambient sound shape",
	category: \misc,
	tags: [\metallic, \bass, \ambient, \pitched]
	)
).add