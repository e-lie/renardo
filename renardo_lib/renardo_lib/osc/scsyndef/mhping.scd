SynthDef.new(\mhping,{
	|bus=0, freq = 0, amp = 1, fmod=0, atk=0.001, sus=1, rel=0.3, curve= -4, pan=0, rate=9, depth=0.02|
	var osc, lfo, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	lfo = LFNoise2.ar(rate).range(1/(1 + depth),(1 + depth));
	env = Env.linen(attackTime: atk, sustainTime: sus, releaseTime: rel, curve: curve).kr(doneAction:0);
	osc = SinOsc.ar(freq: [freq, freq * lfo], mul: env);
	osc = osc * env * amp * 0.1;
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "unknown",
	modified_by: "Bruno Ruviaro, Josh Mitchell",
	decription: "Your basic percussive synth instrument, a good default sound for testing patterns",
	category: \category,
	tags: [\tag, \tag]
)).add;
