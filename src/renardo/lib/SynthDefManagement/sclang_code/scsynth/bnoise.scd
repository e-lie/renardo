SynthDef.new(\bnoise, {
	|bus=0, amp=0.1, freq=10, blur=1, fmod=0, dur=1, gate=1, freq1=1000, freq2=2000, pan=0, sus=1|
	var sig0, sig1, sig2, sig3, osc,  env;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = EnvGen.ar(Env(times: [sus, sus],levels: [0, amp, 0],curve: 'lin'), doneAction: 0);
	sig1 = BPF.ar(BrownNoise.ar(mul: SinOsc.ar(freq, phase: Rand (0, pi), mul: Rand (0.1, 2))), 3 * Rand(0, freq1));
	sig2 = BPF.ar(PinkNoise.ar(mul: SinOsc.ar(freq * 1.1, phase: Rand (0, pi), mul: Rand (0.1, 1))), 2 * Rand(0, freq2));
	sig3 = ({ Mix.fill(5,{Pan2.ar(SinOsc.ar(Gendy4.ar(6.rand,6.rand,SinOsc.kr(0.1,0,0.49,0.51),SinOsc.kr(0.13,0,0.49,0.51),freq ,freq, SinOsc.kr(0.17,0,0.49,0.51), SinOsc.kr(0.19,0,0.49,0.51), 12, 12, 200, 400), 0, 0.1), 1.0.rand2)})});
	sig0 = (((sig1 + sig2 + sig3)) * 8).tanh ;
	osc = sig0 * amp;
	osc = (osc * env);
	osc = HPF.ar(osc, 40);
	osc = LPF.ar(osc, 8000);
	osc = Mix(osc) * 0.2;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "CrashServer",
	modified_by: "",
	description: "",
	category: \category,
	tags: [\tag]
	)
).add;