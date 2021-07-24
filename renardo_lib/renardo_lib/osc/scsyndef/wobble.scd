SynthDef.new(\wobble, {
	|bus=0, amp=1, sus=1, fmod=0, pan=0.0, atk=0.01, rel=0.09, freq=440,
	modfreq=4, width=0.4|
	var osc, osc1, osc2, mod, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	mod = SinOsc.kr(modfreq).range(0, 1);
	osc1 = LFPulse.ar(freq, width: width, mul: mod);
	osc2 = LFTri.ar(freq, mul: mod);
	env = EnvGen.ar(Env.linen(atk, sus, rel, curve: \sin), doneAction: 0);
	osc = Mix([osc1, osc2]);
	osc = osc * env * amp * 0.15;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "gacastillo",
	modified_by: "Jens Meisner",
	decription: "Simple modified Low Filter Triangle Oscillator",
	category: \category,
	tags: [\tag, \tag]
)).add;