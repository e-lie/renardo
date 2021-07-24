SynthDef.new(\tworgan3, {
	|bus=0, pan=0, freq=440, amp=1, fmod=0, atk=0.1, sus=1, rel=0.1, gate=1,
	//Extra attributes
	vrate=6, vdepth=0.02, vdelay=0.1, vonset=0, vratevar=0.1, vdepthvar=0.1, fharm=5.04, rq=1, blend=0.83|
	var osc, env, vibrato;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.linen(atk, sus, rel).kr(gate: gate, doneAction: 0);
	vibrato = Vibrato.kr(freq: freq, rate: vrate, depth: vdepth, delay: vdelay, onset: vonset, rateVariation: vratevar,
		depthVariation: vdepthvar);
	osc = LFPulse.ar(freq: freq, width: 0.5, mul: 1 - blend) + LFPulse.ar(freq: freq + vibrato, width: 0.18, mul: blend);
	osc = BLowPass4.ar(in: osc, freq: fharm * freq, rq: rq, mul: env);
    osc = LeakDC.ar(osc);
	osc = Mix(osc);
	osc = osc * env * amp * 0.15;
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