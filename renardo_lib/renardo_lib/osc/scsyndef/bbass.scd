SynthDef.new(\bbass, {
	|bus=0, freq = 0, amp = 1, pan=0, fmod=0, atk=0.07, sus=1, blur=1|
	var env, oscfreq, osc, envout, lfo;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	sus = sus * blur;
	oscfreq = {freq * LFNoise2.kr(Rand(0.0001, 0.5)).range(0.98, 1.02)}!5;
	lfo = { SinOsc.kr({ 1/Rand(2, 52) }!5) };
	env = Env.adsr(atk, 1, sus, 0.1).kr(doneAction:0);
	osc = LFSaw.ar(oscfreq, mul: lfo.value.range(0,1));
	osc = RLPF.ar(osc,(env*freq) + 1*freq * lfo.value.range(10/freq,5/freq), lfo.value.range(0.1,1));
	osc = Splay.ar(osc, lfo.value.range(0,1));
	envout = EnvGen.ar(Env.perc(level: amp, releaseTime: sus, attackTime: 0.02, curve: 'lin'), doneAction: 0);
	osc = Mix(osc) * 0.02 * envout * amp;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc);
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;