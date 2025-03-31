SynthDef.new(\prayerbell, {
	|bus=0, freq = 0, amp = 1, fmod=0, decayscale=0.6, singswitch=0, lag=3, pan=0|
	var osc, input, first, freqscale, mallet, sing;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freqscale = freq / 2434;
	freqscale = Lag3.kr(freqscale, lag);
	decayscale = Lag3.kr(decayscale, lag);
	mallet = LPF.ar(in: Impulse.ar(0)!2,freq: 8000 * freqscale);
	sing = LPF.ar(in: {PinkNoise.ar * Integrator.kr(singswitch * 0.001, 0.999).linexp(0, 1, 0.01, 1)}!2 * amp, freq:2434 * freqscale);
	sing = sing + Dust.ar(0.15);
	sing = LPF.ar(sing, 10000 * freqscale);
	sing = sing * LFNoise1.kr(0.5).range(-45, -30).dbamp;
	input = mallet/2 + (singswitch.clip(0, 1) * sing);
	osc = DynKlank.ar(
		specificationsArrayRef: `[
			// Array of filter frequencies
			[
				(first = LFNoise1.kr(0.5).range(2424, 2444)) + Line.kr(20, 0, 0.5),
				first + LFNoise1.kr(0.5).range(1,3),
				LFNoise1.kr(1.5).range(5435, 5440) - Line.kr(35, 0, 1),
				LFNoise1.kr(1.5).range(5480, 5485) - Line.kr(10, 0, 0.5),
				LFNoise1.kr(2).range(8435, 8445) + Line.kr(15, 0, 0.05),
				LFNoise1.kr(2).range(8665, 8670),
				LFNoise1.kr(2).range(8704, 8709),
				LFNoise1.kr(2).range(8807, 8817),
				LFNoise1.kr(2).range(9570, 9607),
				LFNoise1.kr(2).range(10567, 10572) - Line.kr(20, 0, 0.05),
				LFNoise1.kr(2).range(10627, 10636) + Line.kr(35, 0, 0.05),
				LFNoise1.kr(2).range(14689, 14697) - Line.kr(10, 0, 0.05)
			],
			// Array of filter amplitudes
			[
				LFNoise1.kr(1).range(-10, -5).dbamp,
				LFNoise1.kr(1).range(-20, -10).dbamp,
				LFNoise1.kr(1).range(-12, -6).dbamp,
				LFNoise1.kr(1).range(-12, -6).dbamp,
				-20.dbamp,
				-20.dbamp,
				-20.dbamp,
				-25.dbamp,
				-10.dbamp,
				-20.dbamp,
				-20.dbamp,
				-25.dbamp
			],
			// Array of filter decay times
			[
				20 * freqscale.pow(0.2),
				20 * freqscale.pow(0.2),
				5,
				5,
				0.6,
				0.5,
				0.3,
				0.25,
				0.4,
				0.5,
				0.4,
				0.6
			] * freqscale.reciprocal.pow(0.5)
		],
		input: input,
		freqscale: freqscale,
		freqoffset: 0,
		decayscale: decayscale
	);
	osc = osc * amp * 0.4;
	DetectSilence.ar(osc,doneAction: 0);
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Wondersluyter",
	modified_by: "Bruno Ruviaro, Jens Meisner",
	decription: "Tibetan prayer bell",
	category: \bells,
	tags: [\percussion, \bell, \prayer, \tibetan]
)).add;
