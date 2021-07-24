SynthDef.new(\click, {
	|amp = 1, freq = 0, bus=0, fmod=0, sus=1, pan = 0, vib=1, mult=4, ptime=0.2|
	var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc = BLowPass.ar(Impulse.ar(vib, 0, vib+4), mult, 0.5);
	osc = osc + LFPar.ar(
		Env.perc(0, ptime).ar.linexp(0, 1, freq, freq * 2) *
		LFDNoise3.kr(4).exprange(fmod.midiratio, 0.1.midiratio),
		-1);
	env = Env([1, 0], sus, -4).kr(2);
	osc = osc * env;
	osc = Mix(osc) * 0.1;
	osc = Pan2.ar(osc, pan);
	osc = Splay.ar(osc * amp);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;