SynthDef.new(\angst, {
	|amp=1, sus=1, gate=1, pan=0, freq=0, vib=0, fmod=0, rate=1, cutoff=18000, rq=0.5, mul=1, bus=0, atk=0.0001, decay=0.01, rel=0.01, level=0.8, peak=1|
	var osc, pulse, filter,env,clip, z;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	clip = LinLin.kr(rate, 0, 1, 2e-12, 2e-1);
	z = SinOsc;
	y = freq;
	osc = GVerb.ar(z.ar(y+z.kr([freq / 4,freq / 2],0,y*LFDNoise1.kr(0.4,1.4).abs))*0.05+GVerb.ar(PinkNoise.ar(Decay2.kr(Dust.kr(1!2))*0.02)));
	env=EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
	osc = BLowPass4.ar(osc,(cutoff*(env.squared))+200+freq,rq);
	osc = Mix(osc*env) * 1.6;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
	},
metadata: (
	credit: "CrashServer",
	modified_by: "",
	description: "",
	category: \bass,
	tags: [\tag]
	)
).add;