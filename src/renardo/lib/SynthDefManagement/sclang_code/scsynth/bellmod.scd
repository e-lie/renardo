SynthDef.new(\bellmod, {
	|amp=1, sus=1, pan=0, freq=0, vib=0,  fmod=0, rate=1, bus=0, lag = 10, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8, wide=0.0, input, s1=1, s2=0, s3=0|
	var osc, env, sig1, sig2, sig3;
	env=EnvGen.ar(Env.perc(attackTime: atk,releaseTime: sus,level: amp,curve: 'lin'), doneAction: 0);
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	sig1=(Klank.ar(`[[0.501, 1, 0.7, 2.002, 3, 9.6, 2.49, 11, 2.571, 3.05, 6.242, 12.49, 13, 16, 24], [0.002, 0.1, 0.001, 0.008, 0.02, 0.004, 0.02, 0.04, 0.02, 0.005, 0.05, 0.05, 0.02, 0.03, 0.04], [1.2, 1.2, 1.2, 0.9, 0.9, 0.9, 0.25, 0.25, 0.25, 0.14, 0.14, 0.14, 0.07, 0.07, 0.07]], Impulse.ar(0.01), freq, 0, (4 * rate)) * amp);
	sig1 = Mix(sig1 * env) * 4;
	sig2=(Klank.ar(`[
[1, 2, 2.803, 3.871, 5.074, 7.81, 10.948, 14.421],
[1, 0.044, 0.891, 0.0891, 0.794, 0.1, 0.281, 0.079],
[1, 0.205, 1, 0.196, 0.339, 0.047, 0.058, 0.047]
], Impulse.ar(0.01), freq, 0, (4 * rate)) * amp);
	sig2 = Mix(sig2 * env) * 0.8;
	sig3=(Klank.ar(`[
[1.013, 1.512, 2.113, 2.525, 3.35, 4.57, 6.48],
[1, 0.78, 0.89, 0.63, 0.31, 0.56, 0.25],
[1, 0.9, 0.8, 0.65, 0.45, 0.3, 0.1]
], Impulse.ar(0.01), freq, 0, (4 * rate)) * amp);
	sig3 = Mix(sig3 * env) * 0.6;
	osc =  (sig1 * s1) +(sig2 * s2) + (sig3 * s3);
	osc = Mix(osc) * 0.5;
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
