SynthDef.new(\faim, {
	|bus=0, amp=1, atk=0.001, decay=0.01, sus=1, rel=0.01, level=0.8, peak=1, gate=1, pan=0, freq=0, fmod=0, vib=0, rate=1, blur=1, beat_dur=1, vibr=0|
	var osc, sig1, sig2, sig3, sig4, sig5, sig6, sig7, sig8, env, env1, env2, env3, env4, env5, env6, env7, env8;
	sus = sus*blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = freq * ((0..1)/1 - 0.5 * 0.0007 + 1);
	env1 = EnvGen.kr(Env([0, 1, 0.051, 0], [0.001, 0.01, 0.8], [4, -8]), 1);
	env2 = EnvGen.kr(Env([0,1,0.051,0],[0.005,0.5,1.5], [0,-8], releaseNode:2), 1);
	env3 = EnvGen.kr(Env([0,1,1,0],[0.01,0.01,0.2], [0,0,-4], releaseNode:2), gate);
	env4 = EnvGen.kr(Env([0,1,0],[0.002,2.8], [0,-4]), 1);
	env5 = EnvGen.kr(Env([0,1,1,0],[0.001,0.1,0.8], [4,0,-4], releaseNode:2), gate);
	env6 = EnvGen.kr(Env([0,1,0],[0.001,3.0], [0,-4]), 1);
	sig1 = SinOsc.ar(freq * 11 + 0) * env1 + (SinOsc.ar(vibr) * env1);
	sig2 = SinOsc.ar(freq * 6 * ( sig1 * 2.5 + 1 )) * env2;
	sig3 = SinOsc.ar(freq * 2 * 1 + 0) * env3;
	sig4 = SinOsc.ar(freq * 1 * ( sig3 * 2.5 + 1 ) + 0) * env4;
	sig5 = SinOsc.ar(freq * 1 * ( sig2 * 2.5 + 1 ) * (sig4 * 2.5 + 1)) * env5;
	sig6 = SinOsc.ar(freq * 2) * env6;
	osc = [sig1, sig2, sig3, sig4, sig5, sig6] * DC.ar([0.0, 0.0, 0.0,  0.0, 0.5, 0.5]);
	osc = osc / 2;
	osc = osc.flop.sum;
	env = EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
	osc = osc * env;
	osc = BLowShelf.ar(osc, 40, 1.0, -12);
	osc = osc * AmpComp.kr(freq);
	osc = Limiter.ar(osc);
	osc = osc.tanh;
	osc = Mix(osc) * amp * 0.05;
	osc = Pan2.ar(osc, pan + [ 0, 0, 0, 0, 0, 0]).sum;
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;