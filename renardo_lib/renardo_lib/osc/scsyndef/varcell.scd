SynthDef.new(\varcell, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=1, bus=0, blur=1, beat_dur=1, atk=0.03, decay=0.03, cutoff=4800, rel=0.09, peak=1, level=0.8|
	var osc, oscl, oscr, sigA, sigB, sigC, env, modul;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
	modul = fmod * SinOsc.kr(rate, add:amp) * Line.kr(0, 1, 7);
	sigA = Pulse.ar(freq + modul, LFNoise2.kr(1).range(0.2, 0.8) );
	sigB = VarSaw.ar(freq + modul);
	sigC = WhiteNoise.ar() * 0.15;
	sigC = LPF.ar(sigC,freq*12);
	osc = SelectX.ar(LFNoise2.kr(2).range(0,2),[sigA, sigB, sigC]);
	osc = Mix(osc) * 0.25;
	osc = osc * amp * env;
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
