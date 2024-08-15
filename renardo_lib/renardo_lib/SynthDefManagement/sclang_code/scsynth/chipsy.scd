SynthDef.new(\chipsy, {
	|bus = 0, freq = 0, amp = 1, fmod=0, atk = 0.001, sus=1, rel=0.009, offnote=0.75, pan = 0|
	var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.linen(atk, sus, rel, curve:\lin).kr(doneAction: 0);
	osc = Mix(LFPulse.ar(freq: freq * [1, offnote], iphase: 0.003, width: 0.5, mul:0.04)).tanh;
	osc = osc * env * amp;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
