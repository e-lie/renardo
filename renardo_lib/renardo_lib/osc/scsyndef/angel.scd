SynthDef.new(\angel, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, rq=0.5, cnoise=0.001, offnote=1.01|
	var osc, env, filter;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = freq * [1, offnote];
	osc = Ringz.ar(ClipNoise.ar(cnoise).dup / (cnoise * 2000), freq * 3);
	osc = RHPF.ar(osc, freq * 2.5, rq);
	env = EnvGen.ar(Env([1, 0.8, 0.5, 0],[0.2 * sus, 0.5 * sus, 0.7 * sus]));
	osc = Mix(osc * env) * amp;
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
