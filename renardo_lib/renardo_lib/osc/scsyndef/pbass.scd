SynthDef.new(\pbass, {
	|bus=0, amp=1, atk=0.001, decay=0.01, sus=1, rel=0.01, level=0.8, peak=1, gate=1, pan=0, freq=0, fmod=0, vib=0, rate=1, blur=1, beat_dur=1|
	var subfreq, subenv, env, pluck, tri, sin, sub, click, sig, osc;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	subfreq = freq / 2;
	subenv = Env.linen(0,sustainTime:sus/2,curve:\lin).kr(doneAction:0);
	env = Env.linen(0,sustainTime:sus/2,curve:\lin).kr(doneAction: 0);
	pluck = Pluck.ar(PinkNoise.ar, 1, 0.2, subfreq.reciprocal) * subenv * 2;
	tri = VarSaw.ar(freq);
	sin = SinOsc.ar(freq);
	sub = (SinOsc.ar([subfreq, subfreq - 2, subfreq + 2]).sum * subenv).tanh;
	click = RLPF.ar(Impulse.ar(0), [2000, 8000], 1).sum * 1000;
	osc = pluck + tri + sub + click;
	osc = RLPF.ar(osc, XLine.ar(freq * 100, freq * 10, sus * 0.8).clip(0,20000));
	osc = osc + (MoogFF.ar(osc, freq * 10, 2.5).clip(0,20000) * 0.1);
	osc = BPeakEQ.ar(osc, 400, 0.5, -9);
	osc = BPeakEQ.ar(osc, 2000, 0.5, 6);
	osc = BHiShelf.ar(osc, 8000, 1, 3);
	osc = BPeakEQ.ar(osc, 200, 1, 3);
	osc = osc * XLine.kr(1, 0.6, 0.1);
	osc = (osc * 1).tanh;
	osc = osc + RLPF.ar(osc, XLine.ar(freq * 20,freq * 10,sus).clip(0,20000)) + sin + sub;
	osc = (osc / 2.3).tanh;
	osc = MoogFF.ar(osc,10000,0.1);
	osc = osc * env * amp * 0.3;
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
