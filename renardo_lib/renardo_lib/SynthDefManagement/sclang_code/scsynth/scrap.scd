SynthDef.new(\scrap, {
	|vib=0, bus=0, slide=0, rate=1, atk=0.01, sus=1, slidefrom=1, fmod=0, amp=1, freq=0, bits=0, pan=0|
	var osc, env, vibr;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc = Line.ar(freq * slidefrom, freq * (1 + slide), sus);
	vibr = Vibrato.kr(osc, rate: vib);
	env = Env.linen(atk, sus, 0.04, curve: -4).kr(doneAction: 0);
	osc = osc * vibr;
	osc = Mix(osc) * 0.5;
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
