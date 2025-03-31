SynthDef.new(\rhodes, {
	|amp=1, sus=1, gate=1, pan=0, freq=0, vib=0, fmod=0, rate=4.85, phase=0.5, cutoff=2000, rq=0.5, mul=1, bus=0, atk=0.0001, decay=0.01, rel=0.01, level=0.8, peak=1|
	var osc, pulse, filter,env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc = Pulse.ar(freq*[1,33.5.midiratio],[0.2,0.1],[0.7,0.3]);
	env=EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
	osc = BLowPass4.ar(osc,(cutoff*(env.squared))+200+freq,rq);
	osc = Mix(osc*env*amp) * 0.2;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "unknown",
	modified_by: "Jens Meisner",
	description: "",
	category: \piano,
	tags: [\pitched, \keyboard, \mda_piano]
	)
).add;
