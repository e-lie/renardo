SynthDef.new(\tworgan3, {
	|bus = 0, pan = 0, freq = 440, amp = 0.45, fmod = 0, atk = 0.1, sus = 1, rel = 0.1, gate = 1,
	//Vibrato Controls
	vrate = 6, vdepth = 0.02, vdelay = 0.1, vonset = 0, vrateVariation = 0.1, vdepthVariation = 0.1,
	//Other controls (blend goes from 0 to 1)
	filterHarmonic = 5.04, rq = 1, blend = 0.83|
	var osc, env, vibrato;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.linen(atk, sus, rel).kr(gate: gate, doneAction: 0);
	vibrato = Vibrato.kr(freq: freq, rate: vrate, depth: vdepth, delay: vdelay, onset: vonset, rateVariation: vrateVariation,
		depthVariation: vdepthVariation);
	osc = LFPulse.ar(freq: freq, width: 0.5, mul: 1 - blend) + LFPulse.ar(freq: freq + vibrato, width: 0.18, mul: blend);
	osc = BLowPass4.ar(in: osc, freq: filterHarmonic * freq, rq: rq, mul: env);
    osc = LeakDC.ar(osc);
	osc = Mix(osc) * 0.5;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Zé Craum",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	description: "Subtractive tonewheel organ with cheap CPU usage",
	category: \organ,
	tags: [\tonewheelorgan, \pitched, \substractive]
	)
).add;