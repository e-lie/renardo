SynthDef.new(\triwave,{
	|bus = 0, pan = 0.0, freq = 0, fmod = 0, amp = 1.0, atk = 0.01, sus = 1, rel = 0.1, lforate = 3, lfowidth = 0.0, cutoff = 400, rq = 0.7|
	var osc1, osc2, vibrato, filter, env, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	vibrato = SinOsc.ar(lforate, Rand(0, 3.0));
	env = Env.linen(atk,sus,rel,curve:\lin).kr(doneAction: 0);
	osc1 = Saw.ar(freq * (1.0 + (lfowidth * vibrato)), 0.5);
	osc2 = Mix.ar(LFTri.ar((freq.cpsmidi + [11.9, 12.1]).midicps));
	osc = RHPF.ar(((osc1 * 0.4) + (osc2 * 0.6)));
	osc = osc * env * amp;
	osc = Mix(osc) * 0.3;
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
