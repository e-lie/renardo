SynthDef(\hnoise, {
	| bus=0, freq=800, gate=1, amp=1, atk=0.01 sus=1, fmod=0, pan=0, rel=0.9, room=0.5, rate=1|
	var env, osc, osc2, cenv;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	cenv = EnvGen.ar(Env.perc(0, 0.02), Dust.kr(SinOsc.kr(0.01).range(1, 10)));
	env = EnvGen.ar(Env.asr(atk, sus, rel), gate, doneAction: 0);
	osc = Henon2DN.ar(freq, freq*2, LFNoise2.kr(1, 0.2, 1.2), LFNoise2.kr(1, 0.15, 0.15) * 12);
	osc = Pan2.ar(osc * cenv);
	osc = PitchShift.ar(osc,0.2,TRand.kr(4, 2, Dust.kr(0.5)));
	osc = CombC.ar(osc, 1, LFNoise1.kr(0.1).range(0.1, 0.3), 4);
	osc2 = RLPFD.ar(LFSaw.ar([osc.range(100, 10000).round(50),osc.range(100, 10000).round(50)], 0, 0.8),1000, 0.8, 0.6, 10);
	osc2 = Decimator.ar(CombC.ar(osc2, 0.1, 0.5, 10), 2020, 3) * 0.0125;
	osc = Mix([osc, osc2 * 1]);
	osc = LeakDC.ar(CombC.ar(Mix.ar([osc,(osc2*LFNoise1.kr(0.01, 0.02).abs)]), 1, LFNoise1.kr(0.1).range(0.01, 0.6), 7, 1));
	osc = LeakDC.ar(CombC.ar(osc, 1, SinOsc.kr(TRand.kr(0, 10)).range(0.0001, 2), 80));
	osc = osc * env * amp;
	//osc = Decimator.ar(osc);
	osc = Normalizer.ar(osc) * 0.5;
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