SynthDef.new(\cs80lead, {
	//Standard Values
	|bus = 0, freq = 440, amp = 1, gate = 1.0, pan = 0, fmod = 0,
	//Amplitude Controls
	atk = 0.3, sus = 0.8, rel = 1.0, dec = 0.8,
	//Filter Controls
	fatk = 0.75, fdec = 0.5, fsus = 0.8, frel = 1.0, cutoff = 200,
	//Pitch Controls
	dtune = 0.002, vibspeed = 4, vibdepth = 0.015, ratio = 0.8, glide = 0.15|
	var env, fenv, vib, ffreq, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	//Envelopes for amplitude and frequency:
	env = Env.linen(atk, sus, rel, curve: \sin).kr(gate: gate, doneAction: 0);
	fenv = Env.adsr(fatk, fdec, fsus, frel, curve: 2).kr(gate: gate, doneAction: 0);
	//Giving the input freq vibrato:
	vib = SinOsc.kr(vibspeed).range(1 / (1 + vibdepth), (1 + vibdepth));
	freq = Line.kr(start: freq * ratio, end: freq, dur: glide);
	freq = freq * vib;
	//See beatings.scd for help with dtune
	osc = Saw.ar([freq, freq * (1 + dtune)], mul: env * amp * 0.05);
	osc = Mix.ar(osc);
	//Sending it through an LPF: (Keep ffreq below nyquist!!)
	ffreq = max(fenv * freq * 12, cutoff) + 100;
	osc = LPF.ar(osc, ffreq);
	osc = Mix(osc);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Mike Hairston",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	description: "Vangelis/Blade Runner lead sound, based on tutorial by meastempo ",
	category: \keyboards,
	tags: [\lead, \modulation, \analog, \cs80, \vangelis, \bladerunner]
)).add;