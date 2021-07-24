SynthDef.new(\ppad, {
	|amp=1, freq=0, gate=1, sus=1, pan=0, vib=0, fmod=0, rate=0, bus=0, blur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
	var osc, osc1, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
	osc = SinOsc.ar(freq);
	osc1 = SinOsc.ar(freq + LFNoise0.ar([400,160]).range(2,24).round(2));
	osc = Mix.ar([osc,osc1]).tanh / 3;
	osc = osc + BPF.ar(PinkNoise.ar([0.4,0.8]),freq,0.1);
	osc = osc * env * amp * 0.3;
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;