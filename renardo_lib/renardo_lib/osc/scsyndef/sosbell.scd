SynthDef.new(\sosbell, {
	//Standard Values
	|freq=440, bus=0, amp=1, fmod=0, pan=0, rel=2, curve=\lin,
	//ring Controls (wobbleDepth goes from 0 to 1)
	ringamp=1, ringrel=0.9, wobbledepth=0.9, wobblemin=0.3, wobblemax=3.8,
	//strike Controls
	strikeamp=1, strikedec=0.05, strikerel=0.09, strikedepth=0.058, strikeharm=4,
	//hum Controls
	humamp=0.7, atk=0.1, sus=1|
	var osc, ring, ringEnv, ringFreqs, strike, strikeEnv, strikeMod, hum, humEnv;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	ringFreqs = [2, 3, 4.1, 5.43, 6.8, 8.21];
	ringEnv = Env.new(levels: [1, 0.3, 0.2, 0], times: [1/3, 1/3, 1/3] * ringrel * rel, curve: curve).kr;
	ring = SinOsc.ar(freq: ringFreqs * freq, mul: Array.series(6, 1, -0.1) * ringEnv);
	ring = ring * LFTri.ar(freq: {Rand(wobblemin, wobblemax)}.dup(6)).range((1 - wobbledepth), 1);
	strikeEnv = Env.new(levels: [1, 0.1, 0], times: [strikedec, strikerel * rel], curve: curve).kr;
	strikeMod = LFNoise1.ar(freq * 36).range(1/ (strikedepth + 1), strikedepth + 1);
	strike = SinOsc.ar(freq: freq * strikeharm * strikeMod, mul: strikeEnv);
	humEnv = Env.new(levels: [0, 1, 0.8, 0], times: [atk, sus, rel*2], curve: curve).kr;
	hum = SinOsc.ar(freq: freq * [1.01, 0.47], mul: humEnv);
	osc = Mix.ar((ring * ringamp) + (strike * strikeamp) + (hum * humamp)) * amp * 0.03;
	DetectSilence.ar(in: osc, doneAction: 0);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Dan Stowell",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	category: \bells,
	tags: [\bell, \percussion, \pitched, \additive, \sos]
)).add;