SynthDef(\waves, {
	| amp=0.5, pan=0, bus=0, freq=220, atk=0.01, rel=0.09, rate=4, gate=1, sus=1, fmod=0, blur=1|
	var env, osc2, osc;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = EnvGen.ar(Env.asr(atk, sus, rel, curve: 'lin'), doneAction: 0);
	osc =  SinOsc.ar(freq * (fmod + 1), 0, freq * (rate + 4) * LFNoise1.kr(10.reciprocal).abs);
	osc2 = SinOsc.ar((freq * fmod) + osc, 0, 0.5);
	osc = SinOscFB.ar(osc2, Gendy5.ar(0.1, 0.4, 0.1, mul: 0.1)) + osc2;
	osc = DelayN.ar(osc2, 0.048, 0.048);
	osc = Mix.arFill(4, { CombN.ar(osc, 0.1, LFNoise1.ar(Rand(0, 0.1), 0.04, 0.05), 15) });
	osc = AllpassN.ar(osc, 0.050, [Rand(0, 0.05), Rand(0,0.05)], 1)!2;
	osc = FreqShift.ar(osc, (freq / 2) * (-1));
	//osc = LPF.ar(osc, 4200);
	osc = HPF.ar(HPF.ar(osc, 50));
	osc = Limiter.ar(osc).tanh;
	osc = (osc * amp) * env;
	osc = Mix(osc) * 0.1;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \noise,
	tags: [\tag]
	)
).add;