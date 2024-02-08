SynthDef.new(\rsaw, {
	|bus = 0, freq = 0, amp = 1, fmod=0, atk = 0.1, rel = 1.2, sus = 1, pan = 0, lofreq = 800, hifreq = 4000|
    var env, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
    env = Env.linen(attackTime: atk,sustainTime: sus, releaseTime: rel, level: amp, curve:\sin).kr(doneAction: 0);
    osc = Saw.ar(freq: freq * [0.99, 1, 1.001, 1.008], mul: env);
	osc = LPF.ar(in: osc,freq: LFNoise0.kr(1).range(lofreq, hifreq));
	osc = osc * env * amp * 0.3;
    osc = Splay.ar(osc);
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
