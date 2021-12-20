SynthDef(\birdy,{
	|bus=0, amp=1, sus=1, fmod=0, pan=0.0, atk=0.01, rel=0.09, freq=440, range=0, noiserate=10|
	var osc, osc2, freqenv, convIn, env, trig, rand;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	rand = LFNoise1.ar(noiserate);
	freq = Latch.kr(rand.range(0, 1).round(0.1), rand) * freq;
	freq = LFCub.ar(LFCub.ar(rand)*rand.range(0, 10)).range(freq, freq*2);
	rand = LFNoise1.ar(noiserate);
	convIn = LinCongN.ar(noiserate);
	env = EnvGen.ar(Env.perc(atk, sus, rel, -2), doneAction: 0);
	freqenv = EnvGen.ar(Env([Rand(1000,3000), Rand(3000, 6000), Rand(1000, 2000), Rand(2000, 5000)], [0.1, 0.01, 0.1]);, 1);
	osc = SinOsc.ar(freq + freqenv, phase: 1.0, mul: 1);
	osc2 = LFCub.ar(Convolution.ar(convIn, convIn));
	osc2 = Formlet.ar(osc2, freq, convIn.abs*0.1, rand.abs);
	osc2 = Normalizer.ar(osc2, 0.9, 0.1) * convIn.abs * LFPulse.kr(LFPulse.kr(rand.abs), 0, rand.abs);
	osc = Mix([osc/2, osc2]);
	osc = osc * env * amp * 0.2;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Unknown",
	modified_by: "Jens Meisner",
	decription: "Bird singer",
	category: \category,
	tags: [\tag, \tag]
)).add;