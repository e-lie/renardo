SynthDef.new(\subbass, {
	//Blend goes from 0 to 1
	|bus=0, amp=1, pan=0, freq = 440, fmod=0, atk = 0.1, sus=1, rel = 0.15, curve = -12, blend = 0.5|
    var env, in, ina, synca, octa, inb, syncb, octb, octave, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
    //A slightly rounded percussive envelope
	env = Env.linen(atk, sus, rel, amp, [curve, -1 * curve]).kr(doneAction: 0);
	//Input wave - To use SinOsc.ar, replace "iphase: 2" with "phase: 3pi/2"
	in = LFPar.ar(freq: freq / 2 , iphase: 1.5);
	//Mirroring the wave around the x-axis
	ina = in.range(-1, 1);
	inb = ina;
	//Two square waves exactly out of phase and an octave below the input wave
	synca = LFPulse.ar(freq: freq, iphase: 3pi / 2);
	syncb = LFPulse.ar(freq: freq, iphase: -3pi / 2);
	//This smoothly swaps between outputting the input wave and its mirror
	octa = ina * synca;
	octb = inb * syncb;
	octave = Mix.ar([octa, octb]);
	//Mixer stage, volume adjustments, envelope, and output
	osc = Mix.ar([octave * blend * 0.15, in * (1 - blend) * 0.25]);
	osc = LeakDC.ar(osc);
	osc = Limiter.ar(in: osc, level: 1);
	osc = osc * env * amp;
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