SynthDef.new(\wsaw, {
	|bus=0, amp=1, gate=1, pan=0, fmod=0, spread=0.8, freq=0, atk = 0.01, sus = 1, rel = 0.3|
	var osc, env, osc1, osc2, osc3;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.linen(atk, sus, rel, curve: \sin).kr(doneAction: 0);
	osc1 = LFSaw.ar(freq * 1 + (0.04 * [1,-1]));
	osc2 = LFSaw.ar(freq * 0.99 );
	osc3 = LFSaw.ar(freq * 1 );
	osc = (osc1 + osc2 + osc3);
	osc = (osc*20).tanh;
	osc = Splay.ar(osc, spread:spread, center:pan);
	osc = osc * env * amp;
	osc = Mix(osc) * 0.08;
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
