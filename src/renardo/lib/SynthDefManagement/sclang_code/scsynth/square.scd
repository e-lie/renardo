SynthDef.new(\square, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, phase=0.5, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
	var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	sus = sus * blur;
	osc = PulseDPW.ar(freq, phase);
	env = EnvGen.ar(Env(times: [0.01, (sus - 0.01), 0.01],levels: [0, 1, 1, 0],curve: 'lin'), doneAction: 0);
	osc = osc * env * (amp/8);
	osc = Mix(osc) * 0.3;
	osc = osc * env * amp;
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