SynthDef.new(\video,
	{|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, fx1=0, fx2=0, fx3=0|
	var osc, env;
	freq = In.kr(bus, 1);
	osc = Mix(osc) * 0.5;
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;

