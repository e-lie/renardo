SynthDef.new(\vinsine, {
	//Standard Definitions
	|bus = 0, amp = 0.2, freq = 440, pan = 0, fmod = 0, atk = 0.001, sus = 1, rel = 0.5, gate = 1,
	//Noise Arguments (mainsDepth is 0 to 1)
	noiseAmp = 0.02, mainsDepth = 0.35, mainsHz = 50,
	//Sine Arguments
	vrate = 2, vdepth = 0.005, sineClip = 0.825|
	var noise, env, osc, vibrato;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.linen(atk, sus , rel, curve: \lin).kr(gate: gate, doneAction: 0);
	noise = PinkNoise.ar(noiseAmp * LFPar.ar(mainsHz * 2).range((1 - mainsDepth), 1));
	noise = noise + LFPar.ar(freq: mainsHz, mul: noiseAmp*0.1);
	vibrato = freq * LFNoise2.ar(vrate).range(1/(1 + vdepth), (1 + vdepth));
	osc = Clip.ar(LFTri.ar(vibrato), -1 * sineClip, sineClip).softclip;
	osc = ((osc * amp) + noise) * env;
	osc = Mix(osc) * 0.3;
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