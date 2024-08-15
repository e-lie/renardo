SynthDef.new(\lfnoise, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
	var osc, env, bitRate;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	amp = amp * 2;
	osc = (Dust2.ar(LinLin.kr(rate, 0, 1, 1, 5), 1) + Crackle.ar(1.95, 0.1) + SinOsc.ar((PinkNoise.ar(0.5) * 7500) + 40, 0, 0.006));
	bitRate = 48000 * LinLin.kr(rate, 0, 1, 0, 3).ceil.reciprocal;
	osc = (Decimator.ar(osc, bitRate, LinExp.kr(rate, 0, 1, 24, 6)) * 0.3) + (osc * 0.7);
	env = EnvGen.ar(Env(times: [(sus / 2), (sus*2)],levels: [0, amp, 0],curve: 'lin'), doneAction: 0);
	osc = (osc * env * 4);
	osc = Mix(osc);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \category,
	tags: [\tag]
	)
).add;

