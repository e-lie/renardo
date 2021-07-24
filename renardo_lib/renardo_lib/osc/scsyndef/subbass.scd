SynthDef.new(\subbass, {
	//Blend goes from 0 to 1
	|bus=0, amp=1, pan=0, freq = 440, fmod=0, atk = 0.01, sus=1, rel = 0.15, curve = -12, blend = 0.5, plpf=2400, plpr=1.0|
    var env, in, ina, synca, octa, inb, syncb, syncc, octb, octave, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = freq / 3;
	amp = amp * 2;
    //A slightly rounded percussive envelope
	env = Env.linen(atk, sus, rel, amp, [curve, -1 * curve]).kr(doneAction: 0);
	//Input wave - To use SinOsc.ar, replace "iphase: 2" with "phase: 3pi/2"
	in = LFPar.ar(freq: freq , iphase: 0.5);
	//Mirroring the wave around the x-axis
	ina = in.range(-1, 1);
	inb = ina;
	//Two square waves exactly out of phase and an octave below the input wave
	synca = LPF.ar(LFSaw.ar(freq: freq / 1, iphase: 0.5, mul: 0.2) + SinOscFB.ar(freq, mul: 1), plpf, plpr);
	syncb = LPF.ar(LFTri.ar(freq: freq / 2, iphase: 0.5, mul: 1.0) + SinOscFB.ar(freq, mul: 1), plpf, plpr) ;

	//This smoothly swaps between outputting the input wave and its mirror
	octa = ina * synca;
	octb = ina * syncb;
	octave = Mix.ar([octa, octb]);
	//Mixer stage, volume adjustments, envelope, and output
	osc = Mix.ar([octave * blend * 0.4, in * (1 - blend)]);
	osc = LeakDC.ar(osc);
	osc = Limiter.ar(in: osc, level: 1);
	osc = osc * env * amp * 0.2;
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