(
SynthDef(\mhpad, {
	//Standard Values:
	|bus = 0, pan = 0, freq = 440, amp = 1, fmod=0, atk = 0.1, dec = 0.05, sus = 1, rel = 1.0, gate = 1,
	//Other Controls:
	vibratoRate = 4, vibratoDepth = 0.02, tremolo=3,
	//These controls go from 0 to 1:
	tremoloDepth = 0.5|
	var env, osc, vibrato, mod2, mod3;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.adsr(atk, dec, sus, rel, peakLevel: 1.08, curve: \sin).kr(gate: gate, doneAction: 0);
	vibrato = SinOsc.kr(vibratoRate).range(freq * (1 - vibratoDepth), freq * (1 + vibratoDepth));
	tremolo = LFNoise2.kr(1).range(0.2, 2) * SinOsc.kr(tremolo).range((2 - tremoloDepth), 1);
	osc = SinOsc.ar(freq: [freq, vibrato], mul: env * tremolo * amp * 0.3).distort;
	osc = Mix.ar([osc]);
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
)