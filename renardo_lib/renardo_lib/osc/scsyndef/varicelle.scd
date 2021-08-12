SynthDef.new(\varicelle, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=1, bus=0, blur=1, beat_dur=1, atk=0.03, decay=0.03, rel=0.09, peak=1, level=0.8,
	cutoff=4800, noisemix=0.5, noiserate=12, xvib=2|
	var osc, oscl, oscr, sigA, sigB, sigC, env, modul;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
	modul = fmod * SinOsc.kr(rate, add: amp) * Line.kr(0, 1, 7);
	sigA = Pulse.ar(freq + modul, LFNoise2.kr(1).range(0.2, 0.8) );
	sigB = VarSaw.ar(freq + modul);
	sigC = LPF.ar(WhiteNoise.ar(noisemix) * 0.15, freq * noiserate);
	sigA = sigA + sigC;
	sigB = sigB + sigC;
	osc = SelectX.ar(LFDNoise3.kr(xvib, 0.5).range(0, 1), [sigA, sigB]);
	osc = Mix(osc);
	osc = osc * env * amp * 0.15;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
