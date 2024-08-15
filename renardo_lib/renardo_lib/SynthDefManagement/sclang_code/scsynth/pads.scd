SynthDef.new(\pads, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, atk=0.1, decay=0.5, rel=0.7|
	var osc, env, filter;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	amp=(amp * 2);
	freq = freq * [1, 1.01];
	osc = SinOsc.ar(Line.kr(freq * 4, freq, 0.01) + (Line.kr(10, (freq * 2), sus) * Pulse.ar(freq * rate, width: SinOsc.kr(0.225/sus))), mul:decay);
	env = EnvGen.ar(Env([0, atk, decay, 0],[atk, decay * sus, rel * sus]));
	osc = RHPF.ar(osc, [Line.kr(400, 1000, sus), Line.kr(4000,900,sus)], decay);
	osc = osc * env * amp * Line.ar(0.001,1,sus * 0.05);
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
