SynthDef.new(\vinsine, {
	|bus=0, amp=1, freq=440, pan=0, fmod=0, atk=0.001, sus=1, rel=0.5, gate=1,
	noiseamp=0.02, mainsdepth=0.35, mainshz = 50, vrate = 2, vdepth = 0.005, sineclip = 0.825|
	var noise, env, osc, vibrato;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.linen(atk, sus , rel, curve: \lin).kr(gate: gate, doneAction: 0);
	noise = PinkNoise.ar(noiseamp * LFPar.ar(mainshz * 2).range((1 - mainsdepth), 1));
	noise = noise + LFPar.ar(freq: mainshz, mul: noiseamp*0.1);
	vibrato = freq * LFNoise2.ar(vrate).range(1/(1 + vdepth), (1 + vdepth));
	osc = Clip.ar(LFTri.ar(vibrato), -1 * sineclip, sineclip).softclip;
	osc = osc + noise;
	osc = Mix(osc);
	osc = osc * env * amp * 0.1;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Zé Craum",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	description: "Crude simulation of old sinusoidal generators - with random vibrato and a high noise floor, 50hz mains hum emulation and slightly distorted sine",
	category: \keyboards,
	tags: [\vintage, \pitched]
)).add;