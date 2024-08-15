SynthDef.new(\longsaw, {
	|amp=1,  atk=0.01, sus=1, rel=0.8, pan=0, freq=0, fmod=0, rate=0, bus=0|
	var osc,  env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	amp = (amp / 10);
	env = EnvGen.ar(Env.linen(atk, sus, rel), doneAction: 0);
	osc = Saw.ar(freq,Line.kr(1, 2, 4), mul: 1);
	osc = (osc * env * amp);
	osc = Mix(osc) * 0.3;
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
