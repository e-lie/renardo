SynthDef(\epiano, {
	//Standard values
	|bus = 0, freq = 440, amp = 1, fmod = 0, atk = 0.1, sus = 1, rel = 0.3, pan = 0,
	//These range from 0 to 1
	tone = 0.5, hollowness = 0.02|
	var hammer, osc, delay, tonefreq, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.perc(atk, sus + rel, amp, -1).ar(doneAction: 0);
	// Delay line times: freq, freq - 4 cents, freq + 3 cents. In the original this was done by converting freq to midi.
	delay = (1 / (freq * [2.pow(-0.04/12), 1, 2.pow(0.03/12)]));
	tonefreq = tone.linlin(0, 1, 1000, 5000);
	hammer = Decay2.ar(in: Impulse.ar(0.001), attackTime: 0.008, decayTime: 0.04,
		mul: LFNoise2.ar(freq: amp.linlin(0, 1, tonefreq, 2 * tonefreq), mul: 0.25));
	//Try LFNoise1, LFNoise0, or even LFClipNoise above for a slightly grainier sound.
	osc = CombL.ar(hammer, delay, delay, 50 * amp);
	osc = HPF.ar(osc, hollowness.linlin(0, 1, 50, 1000));
	osc = osc * env;
	osc = Limiter.ar(osc);
	osc = Mix(osc) * 0.5;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Jeff & James",
	modified_by: "Josh Mithell, Bruno Ruviaro, Jens Meisner",
	description: "based on something posted 2008-06-17 by jeff, based on an old example by james mcc",
	category: \keyboards,
	tags: [\casio, \piano, \pitched]
	)
).add;