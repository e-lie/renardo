SynthDef.new(\varsaw, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, rel=0.01, peak=1, level=0.8,
	offnote=1.005|
	var osc, env;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = (freq * [1, offnote]);
	osc = VarSaw.ar(freq, mul: 0.2, width: rate);
	env = EnvGen.ar(Env.linen(atk, sus, rel, curve: 'lin'), doneAction: 0);
	osc = Mix(osc);
	osc = osc * env * amp * 0.15;
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
