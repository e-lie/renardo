SynthDef.new(\dafbass, {
	|amp=1 pan=0, freq=0, vib=0, fmod=0, ffmod=1, rate=0, bus=0, atk=0.01, dec=0.1, sus=1, rel=0.09, level=0.8, peak=1, offnote=1.01|
	var osc, env, harm;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	//freq = [freq, freq] * Line.ar(Rand(0.5, 1.5), 1, 0.02);
	freq = (freq / 4);
	harm = [1, offnote, 2, offnote * 2];
	harm = harm++(harm*ffmod);
	amp = amp / (ffmod / 0.5);
	osc = (SinOsc.ar(freq*harm).sum.distort * 2) + LFPulse.kr(freq + harm, 0, [0.5, 0.99]).sum.distort;
	env = EnvGen.ar(Env([0, peak, level, level, 0], [atk, dec, max((atk + dec + rel), sus - (atk + dec + rel)), rel], curve:\sin), doneAction: 0);
	osc = Mix(osc) * env * amp * 0.1;
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
