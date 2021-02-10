SynthDef.new(\wobble, {
	|bus=0, amp=1, sus=1, pan=0.0, atk = 0.01, freq=0|
	var osc, env;
	freq = In.kr(bus, 1);
	osc = SinOsc.ar(freq)!2;
	env = EnvGen.ar(Env.perc(attackTime: atk, releaseTime:sus), doneAction: 0);
	osc = osc * env * amp;
	osc = Mix(osc) * 0.3;
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