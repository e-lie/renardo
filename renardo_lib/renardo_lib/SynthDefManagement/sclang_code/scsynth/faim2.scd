SynthDef.new(\faim2, {
	|bus=0, amp=0.1, atk=0.001, decay=0.01, sus=1, rel=0.01, level=0.8, peak=1, gate=1, pan=0, freq=0, fmod=0, vib=0, beef=0, rate=1, blur=1, beat_dur=1|
	var osc, osc1, osc2, osc3, osc4, osc5, osc6, osc7, osc8;
	var env, env1, env2, env3, env4, env5, env6, env7, env8;
	sus = sus*blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = freq / 2;
	freq = freq * ((0..1)/1 - 0.5 * 0.0007 + 1);
	env1 = EnvGen.kr(Env([0,1,0.051,0],[0.001,0.01,0.8], [4,-8]), 1);
	env2 = EnvGen.kr(Env([0,1,0.051,0],[0.005,0.5,1.5], [0,-8], releaseNode:2), 1);
	env3 = EnvGen.kr(Env([0,1,1,0],[0.01,0.01,0.2], [0,0,-4], releaseNode:2), gate);
	env4 = EnvGen.kr(Env([0,1,0],[0.002,2.8], [0,-4]), 1);
	env5 = EnvGen.kr(Env([0,1,1,0],[0.001,0.1,0.8], [4,0,-4], releaseNode:2), gate);
	env6 = EnvGen.kr(Env([0,1,0],[0.001,3.0], [0,-4]), 1);
	osc1 = SinOsc.ar(freq * 11) * env1 + (SinOsc.ar(vib) * env1);
	osc2 = SinOsc.ar(freq * 8 * ( osc1 * 2.5 + 1 )) * env2;
	osc3 = SinOsc.ar(freq * 2) * env3;
	osc4 = SinOsc.ar(freq * 1 * ( osc3 * 2.5 + 1 ) + 0) * env4;
	osc5 = SinOsc.ar(freq * (1+beef) * ( osc2 * 2.5 + 1 ) * (osc4 * 2.5 + 1)) * env5;
	osc6 = SinOsc.ar(freq * 1) * env6;
	env = EnvGen.ar(Env.asr(atk, sus, rel, curve:\sin), gate, doneAction: 0);
	osc = [osc1, osc2, osc3, osc4, osc5, osc6] * DC.ar([0.0, 0.0, (1+beef) / 4,  0.0, 0.5, 1]);
	osc = osc / ( 2 + beef);
	osc = osc.flop.sum;
	// Cutting very low freq
	osc = BLowShelf.ar(osc, 40, 1, -12);
	osc = osc * AmpComp.kr(freq) * 0.65;
	osc = Limiter.ar(osc);
	osc = osc.tanh;
    osc = osc * env * amp;
	osc = Mix(osc) * 0.3;
	osc = Pan2.ar(osc, pan).sum;
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \category,
	tags: [\tag]
	)
).add;
