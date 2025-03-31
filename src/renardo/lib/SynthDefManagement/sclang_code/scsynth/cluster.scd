SynthDef.new(\cluster, {
	|bus=0, gate=1, amp=1, dur=1, pan=0, freq=0, atk=0.01, sus=1, rel=0.009, blur=1, fmod=0, para1=7, mult=4, pstep=0.75|
	var env, osc;
	freq = In.kr(bus,1);
	freq = [freq, freq+fmod];
	sus = sus * blur;
	env = Env.linen(attackTime:atk,sustainTime:sus,releaseTime:rel,curve:\lin).kr(doneAction:0);
	osc = Splay.ar(LeakDC.ar(CombN.ar(SinOsc.ar(1/para1,Spring.ar(LFPulse.ar(pstep), 4 / para1, [[0.5e-1, 1.4e-3]]) * LFTri.ar(freq, 0, 2pi, mult * pi), mul: 0.05), 2, 0, 2))).tanh;
	osc = Mix(osc * env) * amp;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
