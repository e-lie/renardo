SynthDef.new(\tribell,{
	|bus = 0, pan = 0.0, freq = 440, amp = 1.0, gate = 1, fmod = 0, atk = 0.1, sus = 1, rel = 3, lforate = 8, lfowidth = 0.02, cutoff = 80, rq = 0.05|
	var osc1, osc2, vibrato, filter, env, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	vibrato = SinOsc.ar(lforate, Rand(0, 2.0));
	osc1 = Saw.ar(freq * (1.0 + (lfowidth * vibrato)), 0.65);
	osc2 = Mix(LFTri.ar((freq.cpsmidi + [11.9, 12.1]).midicps));
	filter = RHPF.ar((osc1 + (osc2 * 0.8)) * 0.4, cutoff, rq);
	env = EnvGen.ar(envelope: Env.perc(atk, sus + rel, amp), gate: gate, doneAction: 0);
	osc = Mix(osc);
	osc = filter * env * amp * 0.3;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Mitchell Sigman",
	modified_by: "Bruno Ruviaro, Jens Meisner",
	decription: "Description",
	category: \pads,
	tags: [\pitched, \tag]
)).add;