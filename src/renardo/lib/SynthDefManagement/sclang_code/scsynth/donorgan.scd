SynthDef.new(\donorgan,{
	|bus=0, pan=0, freq=440, amp=1, gate=1, fmod=0, atk=0.01, dec=0.5, sus=1, rel=0.5, lforate=9, lfowidth=0.01, cutoff=220, rq=0.5|
	var vibrato, filter, env, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	vibrato = SinOsc.kr(lforate, Rand(0, 2.0));
	freq = freq * [1, 1.9953843530485, 3.0139733629359];
	freq = freq * (1.0 + (lfowidth * vibrato));
	env = EnvGen.ar(Env.linen(atk, sus, rel), gate, doneAction: 0);
	osc = VarSaw.ar(freq, iphase: 1, width: Rand(0.3, 0.5) ! 2, mul: 0.2);
	filter = RLPF.ar(osc, cutoff, rq);
	osc = Mix(osc * env ) * amp * 0.1;
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Mitchell Sigman, Nick Collins",
	modified_by: "Bruno Ruviaro, Jens Meisner",
	decription: "Description",
	category: \organ,
	tags: [\keys, \pulsesynth]
)).add;
