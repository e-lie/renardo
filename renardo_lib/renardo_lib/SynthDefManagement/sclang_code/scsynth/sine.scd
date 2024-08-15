SynthDef.new(\sine, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, rel=0.01, peak=1, level=0.5, sinefb=0.2|
	var osc, env;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc = SinOscFB.ar(freq, sinefb)*0.1;
	env = Env.linen(atk,sus,rel,curve:'lin').kr(doneAction: 0);
	osc = osc * env * amp;
	osc = Mix(osc);
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
