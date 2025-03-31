SynthDef(\prof, {
	|amp=0.3, pan=0, freq=0, vib=0, fmod=0, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, sus=1, rel=0.01, peak=1, level=0.8, gate = 1, rate = 0.1, phase = 0.5, cutoff = 900, rq = 0.5|
	var lfo, osc, filter, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	lfo = LFTri.kr(rate * [1, 1.01], Rand(0, 2.0) ! 2, 1);
	osc = Pulse.ar(freq * [1, 1.01], lfo * phase + 0.5);
	filter = RLPF.ar(osc, cutoff, rq);
	//env = EnvGen.ar(envelope: Env.adsr(atk, decay, sus, rel, amp),gate: gate,doneAction: 2);
	env = EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
	osc = Mix(osc * filter * env);
	osc = osc * amp * 0.8;
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