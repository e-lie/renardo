SynthDef(\sos,
	{|amp=1, gate=1, rel=1,dur=8, bus=0, freq=200, freqs=240,pan=0, fmod=0, sus=1, vib=0|
    var osc1, env, osc, osc2;
    osc1 = VarSaw;
	freqs = (Rand(60, 40)).midicps + SinOsc.ar(Rand(0, 8));
    env = EnvGen.ar(Env(curve: 'lin',levels: [0, amp, 0],times: (sus * 1.2)), doneAction: 0);
	osc = FreeVerb2.ar(*XFade2.ar(
		SinOscFB.ar([Rand(1, 240),Rand(1, 240)], osc1.kr(Rand(1, 400))),
		  SinOscFB.ar([freqs * 1.2,freqs], osc1.kr(vib+1)+Rand(2, 2000)/2), osc1.kr(0.1)));
	osc2 = SinOscFB;
	osc2 = RLPF.ar(BrownNoise.ar(1), Rand(200, 1600), 0.015,1) * 1;
	osc = (osc + (osc2 * Rand(0, 0.01)))  * env;
	// sig = Mix(sig) * 1;
	// sig = LPF.ar(sig, 5000);
	osc = BLowShelf.ar(osc, 60);
	osc = osc * amp * 0.4;
	osc = Pan2.ar(osc, pan).tanh;
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \ambient,
	tags: [\tag]
	)
).add;

