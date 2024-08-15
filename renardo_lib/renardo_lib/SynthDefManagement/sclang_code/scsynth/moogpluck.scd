SynthDef.new(\moogpluck, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.001, decay=0.01, rel=0.01, peak=1, level=0.8, pluckfilter=4, pluckcoef=0.8, pluckmix=0.8|
	var pluck, moog, osc, env;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	pluck =	Pluck.ar(SinOsc.ar(freq * PinkNoise.ar()), 1, freq.reciprocal, freq.reciprocal, sus, coef:pluckcoef.clip(-0.5,0.99));
	pluck = pluck * EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
	moog = MoogFF.ar(pluck, (freq*pluckfilter), 2);
	osc = SelectX.ar(pluckmix,[LPF.ar(pluck, 4300), moog]);
	osc = osc * amp;
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

