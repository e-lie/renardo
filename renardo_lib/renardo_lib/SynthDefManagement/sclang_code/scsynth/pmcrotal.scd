SynthDef.new(\pmcrotal, {
	|bus=0, freq=440, fmod=0, atk=0, sus=1, rel=0.9, curve= -7, amp=1, pan=0, mod=5, atone=2, btone=4|
	var env, osc1, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.linen(atk, sus, rel, curve: curve).kr(doneAction:0);
	osc = PMOsc.ar(freq/2, mod * freq / 2, pmindex: atone, mul: 0.5);
	osc1 = PMOsc.ar(freq/4, freq, pmindex: btone, mul: 0.5);
	osc = HPF.ar(osc, freq, mul: 0.4);
	osc = Mix.ar([osc, osc1]) * 0.2;
	osc = osc * env * amp * 0.4;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "unknown",
	modified_by: "Bruno Ruviarol, Josh Mitchell, Jens Meisner",
	description: "",
	category: \percussion,
	tags: [\pitched, \bell]
	)
).add;