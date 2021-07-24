SynthDef(\mhpad, {
	//Standard Values:
	|bus = 0, pan = 0, freq = 440, amp = 1, fmod=0, atk = 0.1, dec = 0.05, sus = 1, rel = 0.09, gate = 1,
	//Other Controls:
	vibrate = 4, vibdepth = 0.08, trem=2,
	//These controls go from 0 to 1:
	tremdepth = 0.2|
	var env, osc, vibrato, mod2, mod3;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	vibrato = SinOsc.kr(vibrate).range(freq * (1 - vibdepth), freq * (1 + vibdepth));
	trem = LFNoise2.kr(1).range(0.2, 2) * SinOsc.kr(trem).range((1 - tremdepth), 1);
	osc = SinOsc.ar(freq: [freq, vibrato], mul: 1.0).distort;
	env = Env.asr(atk, sus / 2, rel, curve: \sin).kr(gate: gate, doneAction: 0);
	osc = osc * env * amp * 0.15;
	DetectSilence.ar(osc, 0.0001, 0.2, doneAction: 0);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata:(
	credit: "Mike Hairston",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	description: "",
	category: \category,
	tags: [\pad, \vibrato, \sustained]
	)
).add