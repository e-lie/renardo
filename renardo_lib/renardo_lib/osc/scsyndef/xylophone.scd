SynthDef.new(\xylophone, {
	|bus=0, freq=0, fmod=0, amp=1, gate=1, pan=0,
	t60=2|
	var osc, exciter;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	exciter = WhiteNoise.ar() * Env.perc(0.001, 0.07).kr(doneAction: 0) * 0.02;
	osc = DynKlank.ar(
		`[
			[1,2,2.803,3.871,5.074,7.81,10.948,14.421],   // freqs
			[1,0.044,0.891,0.0891,0.794,0.1,0.281,0.079], // amplitudes
			[1,0.205,1,0.196,0.339,0.047,0.058,0.047] * t60 // ring times
		],
		exciter, freq);
	osc = Mix(osc);
	osc = osc * amp * 0.15;
	DetectSilence.ar(osc, 0.001, 0.65, doneAction: 0);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Nicola Ariutti",
	modified_by: "Zé Craum, Jens Meisner",
	description: "",
	category: \bells,
	tags: [\xylophone, \pitched, \glockenspiel]
)).add;

