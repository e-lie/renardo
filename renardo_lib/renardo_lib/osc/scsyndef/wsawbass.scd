SynthDef.new(\wsawbass, {
	|bus = 0, freq = 0, amp = 1, pan = 0, fmod=0, atk = 0.01, sus = 1, rel = 0.3, slideTime = 0.08, cutoff = 1100, width = 0.15, detune = 1.002, preamp = 4|
	var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.linen(atk,sus,rel,curve:\sin).kr(doneAction: 0);
	freq = Lag.kr(freq,slideTime);
	osc = VarSaw.ar(freq: [freq, freq * detune], width: width, mul: preamp);
	osc = Mix(osc,0.7).distort * 0.2;
	osc = LPF.ar(osc, cutoff, amp);
	osc = osc * env * amp;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "James Harkins",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	description: "",
	category: \bass,
	tags: [\bass, \synth, \pitched]
	)
).add;
