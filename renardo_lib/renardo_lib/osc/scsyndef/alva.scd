SynthDef.new(\alva, {
	|bus=0, amp=1, freq=240, pan=0, gate=1, dur, fmod=0, vib=0, sus=1, blur=1, wide|
	var osc, env, freqenv, freqenv2, line;
	freqenv  = EnvGen.ar(Env.new([freq, freq, 40], [0.01, 0.4, dur]));
	freqenv2 = EnvGen.ar(Env.new([freq*1.2, 10, 10], [0.05,  0.25, dur]));
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc = SinOsc.ar(freqenv, VarSaw.kr(0), 4) - SinOscFB.ar(freqenv2/0.2, fmod + 1, freq, 2);
	env=EnvGen.ar(Env(times: [(sus * 0.25), (sus * 1)],levels: [0, amp, 0],curve: 'lin'), doneAction: 0);
	osc=(osc * amp * env);
	//osc = Mix(osc);
	osc = Limiter.ar(osc);
	osc = Mix(osc) * 0.13;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
	},
metadata: (
	credit: "CrashServer",
	modified_by: "",
	description: "",
	category: \bass,
	tags: [\tag]
	)
).add;