SynthDef.new(\siren, {
	|bus=0, slide=0, rate=1, slidefrom=1, atk=0.01, sus=1, fmod=0, amp=1, freq=0, bits=0, pan=0, vib=0, offnote=1.005|
	var osc, osc2, env;
	freq = [freq, freq + fmod];
	freq = Line.ar(freq * slidefrom, freq * (1 + slide), sus);
	freq = Vibrato.kr(freq, rate: vib);
	osc = VarSaw.ar([freq, (freq * offnote)], width: ((rate - 1) / 4));
	osc2 = LFSaw.ar(freq + LFNoise0.ar((rate * 20), mul: 0.5, add: (freq * Pulse.ar(((rate - 2) + 0.1), add: 1))));
	env = EnvGen.ar(Env.perc(attackTime: 0.1, releaseTime: sus, level: amp, curve: \sin), doneAction: 0);
	osc = Mix(osc, osc2) * env * amp * 0.1;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
