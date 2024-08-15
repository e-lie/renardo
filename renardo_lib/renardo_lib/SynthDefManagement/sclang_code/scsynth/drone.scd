SynthDef.new(\drone, {
	|bus = 0, amp = 1, atk=0.01, pan=0, sus = 1, dur = 1, freq=0, gate=1, hpf2=40, fmod=0, speed = 2, lfnoise=80|
	var osc, sig, env;
	freq = In.kr(bus, 1);
	freq = (freq / 2);
	sig = LFNoise1;
	env = EnvGen.ar(Env.linen(atk, sus, 0.5, 0.1, curve:\lin), gate, doneAction:0);
	osc = HPF.ar(
		FreeVerb2.ar(*XFade2.ar(
			SinOscFB.ar([freq, freq], sig.ar(speed) + 0.5),
			SinOscFB.ar([freq, freq + fmod], sig.ar(speed * 2)), sig.ar(lfnoise)))
		, hpf2);
	osc = LeakDC.ar(osc, 0.995);
	osc = Limiter.ar(osc, 0.8);
	osc  = Mix(osc * env) * amp;
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
