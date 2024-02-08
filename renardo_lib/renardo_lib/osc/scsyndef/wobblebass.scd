SynthDef.new(\wobblebass, {
	|bus=0, amp=1, sus=1, fmod=0, pan=0.0, atk=0.01, rel=0.09, freq=440,
	modfreqlo=1, modfreqhi=6, gate=1, wfmax=8500, reso=0.4, iphase=0.0, offnote1=0.98, offnote2=1.025|
	var osc, mod, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = freq / 2;
	osc = MoogVCF.ar(in: (Pulse.ar([freq * offnote1, freq], mul:0.5) + PinkNoise.ar(LFNoise0.ar(2).range(0, 1.0)) + Saw.ar([freq, freq * offnote2], mul: 2)).clip2(1), fco: LFCub.kr(freq: LFPulse.kr(0.5, iphase, width: 0.25).range(modfreqlo, modfreqhi)).exprange(40, wfmax), res: reso, mul: 1);
	env = EnvGen.ar(Env.linen(atk, sus, rel, curve: \sin), doneAction: 0);
	osc = Mix(osc);
	osc = osc * env * amp * 0.2;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Luka P.",
	modified_by: "Jens Meisner",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;