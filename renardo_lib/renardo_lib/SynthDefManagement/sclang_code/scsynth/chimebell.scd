SynthDef.new(\chimebell, {
	|bus=0, atk=0.01, rel=0.02, freq=0, t60=8, offnote=1.001, fmod=0, amp=1, pan=0|
	var osc, env, exciter;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.perc(atk, rel, curve:\sin).kr(doneAction:0);
	exciter = WhiteNoise.ar() * env;
	osc = DynKlank.ar(
		`[
			[1, 2, 2.803, 3.871, 5.074, 7.81, 10.948, 14.421],   // freqs
			[1, 0.044, 0.891, 0.0891, 0.794, 0.1, 0.281, 0.079], // amplitudes
			[1, 0.205, 1, 0.196, 0.339, 0.047, 0.058, 0.047] * t60     // ring times
		], exciter,freqscale: freq, freqoffset: offnote);
	DetectSilence.ar(osc, 0.001, 0.75, doneAction:0);
	osc = Mix(osc) * 0.0001 * amp;
	osc = Pan2.ar(osc,pan,amp);
	Out.ar(bus,osc);
},
metadata: (
	credit: "http://sccode.org/1-5aD",
	modified_by: "Jens Meisner",
	decription: "Description",
	category: \bells,
	tags: [\pitched, \tag]
)).add;
