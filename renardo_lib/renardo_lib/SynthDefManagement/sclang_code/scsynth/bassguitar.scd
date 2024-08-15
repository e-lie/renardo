SynthDef.new(\bassguitar, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.001, decay=0.01, rel=0.01, pick=0.414, rq = 0.5, cutoff = 250|
	var exciter, freqArray, ampArray, decArray, constant, mute, osc, openFreq, pickupPos, pickupWidth, decayCoef, dampCoef;
	openFreq = 82.5;
	pickupPos = 17*decay;
	pickupWidth = 0.75;
	decayCoef = 0.125;
	dampCoef = 0.0002;
	sus = sus*blur;
	freq = In.kr(bus, 1);
	freq = freq/4;
	freq = [freq, freq+fmod];
	constant = pickupWidth/25.5;
	constant = constant * pi/2;
	constant = constant/82.5;
	freqArray = Array.fill(10, {arg i; (i + 1) * sqrt(1 + ((i + 1).pow(2) * 0.00001))});
	freqArray = freqArray/freqArray[0];
	decArray = Array.fill(10, {arg i;
		exp((-1 * i)/((1/decayCoef) + ((dampCoef/10) * freq.pow(2)) + (dampCoef * freqArray[i].pow(2))))});
	decArray = decArray/decArray[0];
	freqArray = freqArray * freq;
	ampArray = Array.fill(10, {arg i;
		((1 - ((freqArray[i] - 19000)/1000).tanh)/2) *
		sin(((i + 1) * pi) * pick) *
		(
			sin(pi * pickupPos * freqArray[i]/openFreq) *
			(
			    (
					sin(constant * freqArray[i])/
					(constant * freqArray[i])
				) - cos(constant * freqArray[i])
			)
		)/(freqArray[i].pow(2))
	});
	ampArray = ampArray * 2/(constant.pow(2));
	exciter = Impulse.ar(0) * 1;
	osc = Klank.ar(specificationsArrayRef: Ref.new([freqArray, ampArray, decArray]), input: exciter, decayscale: sus*2 + rel);
	osc = Mix.ar(osc);
	osc = RLPF.ar(in: osc, freq: cutoff, rq: rq);
	osc = LPF.ar(in: osc, freq: 250);
	mute = Env.new(levels: [1, 1, 0, 0], times: [rel+sus, 0.05, 0.01]).ar(doneAction: 2);
	osc = LPF.ar(in: osc, freq: LinExp.ar(in: mute, srclo: 0, srchi: 1, dstlo: 20, dsthi: 20000));
	osc = osc * amp;
	osc = osc.tanh;
	osc = LeakDC.ar(osc);
	osc = Limiter.ar(osc);
	ReplaceOut.ar(bus, Pan2.ar(osc, pan));
},
metadata: (
	credit: "by Josh Mitchell",
	category: \guitar,
	tags: [\pitched, \modal]
)
).add;

