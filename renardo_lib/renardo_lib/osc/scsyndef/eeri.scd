SynthDef.new(\eeri, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, cutoff=400, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
	var osc, env;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	sus = (sus * 1.75);
	amp = (amp * 2);
	freq=Vibrato.kr(freq, (rate + 4));
	osc = 	 RLPF.ar(SinOsc.ar(Saw.ar([1, 2]).range(1, 104)) * SyncSaw.ar(SinOsc.ar(0.01).range(1, 100), SinOsc.ar(0.01).range(freq, freq*2)), Line.ar(cutoff, freq, 1));
	osc = 	GVerb.ar(osc + CombL.ar(osc, 0.3, 1, 1), 10);
	env = EnvGen.ar(Env(times: [(sus / 2), (sus / 2)],levels: [0, amp, 0],curve: 'lin'), doneAction: 0);
	osc = (osc * env);
	// osc = DWGReverb3Band.ar(osc, 10);
	osc = Mix(osc) * 1/16;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
	},
metadata: (
	credit: "CrashServer",
	modified_by: "",
	description: "",
	category: \noise,
	tags: [\tag]
	)
).add;

