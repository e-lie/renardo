SynthDef.new(\wsaw, {
	|bus=0, amp=1, gate=1, pan=0, fmod=0, spread=0.8, freq=0, atk = 0.01, sus = 1, rel = 0.3,
	iphase1=0.4, iphase2=0.5, iphase3=0.0, offnote1=1, offnote2=0.99, offnote3=1.005|
	var osc, env, osc1, osc2, osc3;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	amp = amp / 10;
	env = Env.linen(atk, sus, rel, curve: \sin).kr(doneAction: 0);
	osc1 = LFSaw.ar(freq * offnote1 + (0.04 * [1,-1]), iphase: iphase1, mul: 1/8);
	osc2 = LFSaw.ar(freq * offnote2, iphase: iphase2, mul: 1/8);
	osc3 = LFSaw.ar(freq * offnote3, iphase: iphase3, mul: 1/8);
	osc = (osc1 + osc2 + osc3);
	osc = (osc * 20).tanh;
	osc = Mix(osc);
	osc = Splay.ar(osc, spread:spread, center:pan);
	osc = osc * env * amp * 0.2;
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
