SynthDef.new(\phazer, {
    |bus = 0, pan = 0, freq = 0, amp = 1, gate = 1, fmod=0, atk = 1, sus = 1, rel = 1.5, crv = -4,
    rq = 0.2, rate = 3, minfreq = 100, maxfreq = 4000, drylevel = 1.2, fmdepth = 0.8|
	var env, lfo, osc, fmfreq;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	fmfreq = freq - 8;
	env = Env.linen(attackTime: atk,sustainTime: sus, releaseTime: rel,curve: crv).kr(doneAction: 0);
	lfo = LinExp.ar(LFTri.ar(rate), -1, 1, minfreq, maxfreq/8);
	osc = LFSaw.ar(freq: SinOsc.ar(fmfreq).range(1, fmdepth) * freq);
	osc = BAllPass.ar(osc, [1, 2, 4, 8] * lfo, rq);
	osc = Mix.ar(osc);
	osc = osc + (osc * -1 * drylevel) * 0.3;
	osc = osc * env * amp;
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Josh Mitchell",
	modified_by: "Jens Meisner",
	category: \misc,
	tags: [\pitched, \effects]
	)
).add;
