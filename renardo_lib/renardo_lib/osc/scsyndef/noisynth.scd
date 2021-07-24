SynthDef.new(\noisynth, {
	|freq = 0, amp = 1, fmod=0, atk = 0.07, sus = 1, pan = 0, bus = 0|
	var env, osc, lfo;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc = {freq * LFNoise2.kr(Rand(0.0001,0.5)).range(0.98, 1.02)}!12;
	lfo = { SinOsc.kr({ 1/Rand(2,52) }!2) };
	env = Env.linen(atk, sus, 0.9, 0.2, curve:\sin).kr(doneAction:0);
	osc = LFSaw.ar(osc, mul: lfo.value.range(0, 1));
	osc = Splay.ar(osc, lfo.value.range(0, 1));
	osc = osc * env * amp * 0.3;
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;