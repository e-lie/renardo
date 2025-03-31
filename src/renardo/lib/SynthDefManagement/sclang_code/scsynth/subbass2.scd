SynthDef.new(\subbass2, {
	//Blend goes from 0 to 1
	|bus=0, amp=1, pan=0, freq=440, fmod=0, atk=0.01, sus=1, rel=0.9, curve= \sqr, blend=0.1, plpf=800, plpr=1.0|
    var env, in, ina, synca, octa, inb, syncb, octb, octave, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = freq / 2;
	//A slightly rounded percussive envelope
	env = Env.linen(atk, sus, rel, amp, [curve, -1 * curve]).kr(doneAction: 0);
	/*  Input wave +/- 90 degrees - To use SinOsc.ar, replace:
	        -"iphase:  0" with "phase: pi/2"
	        -"iphase:  1" with "phase: 0"
	        -"iphase: -1" with "phase: pi"   */
	in = LFPar.ar(freq: freq, iphase: pi/2);
	ina = LFPar.ar(freq: freq, iphase: 0);
	inb = LFPar.ar(freq: freq, iphase: pi);
	//Two square waves exactly out of phase and an octave below the input wave
	synca = LPF.ar(LFPulse.ar(freq: freq / 2, iphase: 0, mul: 0.4) + LFCub.ar(freq: freq, iphase: 0), plpf, plpr);
	syncb = LPF.ar(LFPulse.ar(freq: freq / 2, iphase: 0, mul: 0.4) + LFCub.ar(freq: freq, iphase: 0.5), plpf, plpr);
	//This smoothly swaps between outputting the +90 degree wave and -90 degree wave
	octa = ina * synca;
	octb = inb * syncb;
	octave = Mix.ar([octa, octb]);
	//Mixer stage, volume adjustments, envelope, and output
	osc = Mix.ar([octave * blend, in * (blend - 1)]);
    osc = LeakDC.ar(osc);
	osc = Limiter.ar(in: osc, level: 1);
	osc = osc * env * amp * 0.8;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Josh Mitchell",
	modified_by: "Jens Meisner",
	description: "",
	category: \bass,
	tags: [\pitched, \sub]
	)
).add;