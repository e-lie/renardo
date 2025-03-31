SynthDef.new(\tubularbell, {
	|freq=440, amp=1, pan=0, bus=0, fmod=0, atk=0.1, sus=1, rel=9, exciterRel=0.05|
	var env, osc, exciter;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	amp = amp / 10;
	env = Env.perc(atk, exciterRel, 0.05).kr;
	exciter = GrayNoise.ar(env);
	osc = DynKlank.ar(
		specificationsArrayRef:
	        	Ref.new([
	        		[1.013, 1.512, 2.113, 2.525, 3.35, 4.57, 6.48],   // harmonics
			        [1, 0.78, 0.89, 0.63, 0.31, 0.56, 0.25], // amplitudes
		        	[1, 0.9, 0.8, 0.65, 0.45, 0.3, 0.1]     // ring times
		        ]),
		input: exciter,
		freqscale: freq,
		decayscale: sus + rel
	);
	osc = Mix.ar(osc);
	osc = osc * amp * 0.4;
	DetectSilence.ar(in: osc, amp: 0.001, time: 0.5, doneAction: 0);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "nicolaariutti, Zé Craum",
	modified_by: "Josh Mitchell, Bruno Ruviaro, Jens Meisner",
	description: "",
	category: \bells,
	tags: [\pitched, \tubular, \bell]
)).add;