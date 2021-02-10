SynthDef.new(\drone, {
	|bus = 0, speed = 2, amp = 1, atk=0.08, pan=0, sus = 1, dur = 1, freq=0, gate=1, hpf=40, fmod=0, vib=0|
	var osc, sig, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	sig = LFNoise1;
	env = EnvGen.ar(Env.linen(atk, sus, 0.28, 0.1, curve:\lin), gate, doneAction:0);
	osc = HPF.ar(FreeVerb2.ar(*XFade2.ar(SinOscFB.ar([freq,freq],sig.ar(speed*2)+1),SinOscFB.ar([freq,freq + fmod],sig.ar(speed)+vib),sig.ar(80))),hpf);
	osc = LeakDC.ar((osc * 0.8).tanh, 0.999);
	osc = osc * env;
	osc  = Mix(osc) * amp;
	osc = Limiter.ar(osc, 0.99);
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
