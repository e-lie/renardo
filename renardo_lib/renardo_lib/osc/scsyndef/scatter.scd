SynthDef.new(\scatter, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=1, bus=0, blur=1, beat_dur=1, atk=0.08, rel=0.09,  peak=1, level=0.8, offnote1=2, offnote2=1|
	var osc, env;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc = ((Saw.ar(freq, mul: 0.3) + VarSaw.ar((freq + [offnote1, offnote2]), mul: 0.3))) + LFNoise2.ar(freq, mul:0.3);
	env = EnvGen.kr(Env.asr(atk, sus, rel, curve: \lin), doneAction: 0);
	osc = osc * env * amp;
	osc = Mix(osc) * 0.3;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Jens Meisner",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
