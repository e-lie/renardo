SynthDef.new(\dopple, {
	|amp=1, sus=1, pan=0, freq=440, vib=0, fmod=0, bus=0, blur=1, gate=1, rate=1|
	var osc, env, osc1, osc2, osc3, ffreq, sig1;
	var buf = LocalBuf(2*s.sampleRate, 2);
	var choosetrig;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	ffreq = Sweep.kr(Impulse.kr(1/rate), 1/rate) * 10000;
	osc1 = LFSaw.ar(freq * 1 + (0.04 * [1,-1]));
	osc2 = LFSaw.ar(freq * 0.99);
	osc3 = LFSaw.ar(freq * 1 );
	env = EnvGen.ar(Env(times: [(sus / 2), (sus / 2)],levels: [0, amp, 0], curve: 'lin'), doneAction: 0);
	osc = osc1 + osc2 + osc3;
	osc = (osc*50).tanh;
	osc = osc *env;
	sig1 = RLPF.ar(osc, ffreq, 0.5);
	RecordBuf.ar(sig1, buf, loop:1, trigger:0);
	rate = EnvGen.kr(Env([1,1,1],[0,1], -3), 0);
	osc = sig1;
	osc = Limiter.ar(osc).softclip;
	osc = Mix(osc) * 1/16;
	osc = Pan2.ar(osc * amp, pan);
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
