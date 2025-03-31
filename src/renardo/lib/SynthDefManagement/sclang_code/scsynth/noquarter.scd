SynthDef.new(\noquarter, {
	// Standard Arguments
	|bus = 0, freq = 440, amp = 1, pan = 0, fmod=0, atk = 0.1, sus=1, rel = 1, curve = -1|
	var subfreq, env, pluck, tri, sin, sub, click, osc, subenv;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	subfreq = freq / 2;
	// Envelopes
	subenv = Env.linen(attackTime: atk, sustainTime: sus, releaseTime: rel, level: amp, curve: curve).kr(doneAction: 0);
	env = Env.linen(atk, sus, rel, amp, curve).kr(doneAction: 0);
	// Component synthesis
	pluck = Pluck.ar(in: PinkNoise.ar, trig: 1,	maxdelaytime: 0.8, delaytime: subfreq.reciprocal) * subenv * 2;
	tri = VarSaw.ar(freq) * env;
	sin = SinOsc.ar(freq) * env;
	sub = (SinOsc.ar([subfreq, subfreq - 4, subfreq + 4]).sum / subenv).tanh;
	click = RLPF.ar(in: Impulse.ar(0), freq: [900, 2000], rq: 0.5).sum * 1000;
	// Initial signal
	osc = pluck + tri + sub + click;
	// Resonant LPFs
	//osc = RLPF.ar(in: osc, freq: XLine.ar(freq * 90, freq * 20, 0.05));
	osc = osc + (MoogFF.ar(in: osc, freq:  freq * 100, gain: 2.5) * 0.3);
	// EQ resulting signal
	osc = BPeakEQ.ar(osc, 400, 0.5, -9);
	osc = BPeakEQ.ar(osc, 2000, 0.5, 6);
    osc = BHiShelf.ar(osc, 8000, 1, 3);
	osc = BPeakEQ.ar(osc, 200, 1, 3);
	// Apply another envelope to dampen a bit more
	osc = osc * XLine.kr(1, 0.6, 0.1);
	// Tanh distortion / limiting
	osc = (osc * 1).tanh;
	// Another round of signal coloring, using another RLPF
	// and sine components
	osc = osc + RLPF.ar(in: osc, freq: XLine.ar(freq * 100, freq * 10, 0.15)) + sin + sub;
	// Another round of tanh distortion / limiting
	osc = (osc / 2.3).tanh;
	// Another resonant LPF
	osc = MoogFF.ar(in: osc, freq: XLine.ar(freq*150, freq*30, 0.1), gain:  0.1);
	osc = Pan2.ar(osc, pan) * amp * 0.15;
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Eric Sluyter",
	modified_by: "Jens Meisner",
	description: "",
	category: \bass,
	tags: [\pitched, \bass, \karplus]
)).add;