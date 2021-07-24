SynthDef.new(\risseto, {
	|bus=0, freq = 440, fmod=0, atk = 0.1, sus=1, rel = 1, amp = 1, pan = 0|
    var partials, durs, amps, osc, env, pulsefreq;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	pulsefreq = (freq / 100).trunc(1) ;
 	partials = [246.4, 247.4, 404.8, 406.5, 523.6, 748, 880, 1206, 1320, 1654, 1791]; // original freqs
	partials = partials / freq * 0.5; // consider 440 the 'root'
	durs = [11, 10, 7, 6, 4, 3.4, 3, 2.2, 2, 1.1, 1] / 11;
	amps = durs.linlin(1, 11, 0.2, 1);
	env = Env.linen(attackTime: atk, sustainTime: sus, releaseTime: durs * rel, level: amps).kr(doneAction: 0);
	osc = Pulse.ar(Mix.ar([freq, partials])) * env * amp / 13;
	osc = RLPF.ar(in: osc, freq: freq * LFPulse.ar(pulsefreq).range(2, 4), rq: SinOsc.ar(LFNoise2.kr(1).range(4, 9)).range(0.1, 0.3));
	osc = LPF.ar(osc, 12000);
	osc = Limiter.ar(Mix.ar(osc));
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "by Bruno Tucunduva Ruviaro, based on Jean-Claude Risset's bell",
	modified_by: "Jens Meisner",
	description: "Pulse synth after Risset bell + the higher the pitch, the higher the frequency of pulse",
	category: \pads,
	tags: [\pulsesynth, \bell, \harmonic, \pitched]
)).add;