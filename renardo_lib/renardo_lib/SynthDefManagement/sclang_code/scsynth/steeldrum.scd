SynthDef.new(\steeldrum, {
	|bus=0, freq=440, amp=1, pan=0, fmod=0, atk=0.01, sus=1, curve = -6, fharm=6, offnote=2.015|
	var osc, resFreqArray, resAmpArray, resDecArray, enva, envb, envc, osca, oscb, oscc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	resFreqArray = [2, 2.98, 4.75, 6.21, 9, 9.15, 11.87];
	resAmpArray = [0.35, 0.23, 0.10, 0.06, 0.07, 0.05, 0.01];
	resDecArray = [0.86, 0.72, 0.37, 0.55, 0.32, 0.21, 0.16];
	enva = Env.pairs([[0, 0], [atk, 1], [(atk + sus), 0]], curve).kr;
	envb = Env.pairs([[0, 0], [(atk * 5), 0.25], [(atk * 6), 0.75], [((atk * 6) + (sus)), 0]], curve).kr;
	envc = Env.pairs([[0, 0], [(atk * 5), 0.1], [(atk * 8), 0.5], [((atk * 8) + (sus*1.2)), 0]], curve).kr;
	osca = SinOsc.ar(freq: freq, mul: enva);
	oscb = SinOsc.ar(freq: freq * offnote, mul: envb);
	oscc = DynKlank.ar(specificationsArrayRef:Ref.new([resFreqArray * freq, resAmpArray, resDecArray * sus
	]),input:LPF.ar(HPF.ar(CombN.ar(PinkNoise.ar(1), 1/freq, 1/freq, -1, envc), freq * 2), freq * fharm));
	osc = Mix.ar([osca, oscb, oscc]) * amp * 0.1;
	osc = Limiter.ar(osc, amp);
	DetectSilence.ar(in: osc, amp: 0.0001, time: 0.5, doneAction: 0);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Josh Mitchell",
	modified_by: "Jens Meisner",
	description: "",
	category: \percussion,
	tags: [\pitched, \steelDrum, \steelPan]
)).add;
