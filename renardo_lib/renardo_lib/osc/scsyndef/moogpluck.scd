SynthDef.new(\moogpluck, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.001, decay=0.01, rel=0.01, peak=1, level=0.8, pluck_filter=4,pluck_coef=0.8, pluck_mix=0.8|
	var pluck, moog, osc, env;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	pluck =	Pluck.ar(PinkNoise.ar,1,freq.reciprocal,freq.reciprocal,sus,pluck_coef.clip(-0.5,0.99));
	pluck = pluck * EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel],curve:\sin), doneAction: 0);
	moog = MoogFF.ar(pluck, (freq*pluck_filter),2);
	osc = SelectX.ar(pluck_mix,[LPF.ar(pluck,4300),moog]);
	osc = Mix(osc) * 2;
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

