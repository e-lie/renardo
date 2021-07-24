SynthDef.new(\tworgan2, {
	//Standard Values
	|bus=0, pan=0, freq=440, amp=1, fmod=0, atk=0.001, sus=1, rel=0.1, gate=1,
	//Other controls (blend goes from 0 to 1)
	vibrate=6.0, vibharm=1.017, fharm=5.04, rq=1, blend=0.83|
	var osc, env, vibrato;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.linen(atk, sus, rel, curve: \sin).kr(gate: gate, doneAction: 0);
	vibrato = SinOsc.ar(freq: vibrate).range(freq, freq * vibharm);
	osc = LFPulse.ar(freq: freq, width: 0.5, mul: 1 - blend) + LFPulse.ar(freq: freq + vibrato, width: 0.18, mul: blend);
	osc = RLPF.ar(in: osc, freq: fharm * freq, rq: rq, mul: env);
	osc = osc * amp * 0.15;
    osc = LeakDC.ar(osc);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Zé Craum",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	description: "Subtractive tonewheel organ with cheep CPU usage",
	category: \organ,
	tags: [\tonewheelorgan, \pitched, \substractive]
	)
).add;