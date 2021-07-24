SynthDef.new(\benoit, {
	|bus=0, amp=1, freq=440, fmod=0, semione=12, semitwo=24, trackmul=2, width=0.17, gate=1, sus=1, rel=1, pan = 0|
	var env, osc, osc1, osc2, osc3, osc4, ringmod, tracking;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc1 = Pulse.ar(freq, width);
	osc2 = Pulse.ar((freq.cpsmidi - semione).midicps, width);
	osc3 = Pulse.ar((freq.cpsmidi + semitwo).midicps, width);
	osc4 = LFTri.ar((freq.cpsmidi - semitwo).midicps);
	env = EnvGen.ar(Env.linen(0,sus,rel), gate, doneAction:0);
	tracking = ((freq * 1.01) + freq) * trackmul;
	osc = (osc1 + osc2 + osc3 + (osc4 * 2))/2;
	osc = RLPF.ar(osc, tracking, 1, 0.33);
	osc = osc.tanh;
	osc = osc * env * amp * 0.2;
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