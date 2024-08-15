SynthDef.new(\ssaw, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, sawmix=0.75, sawtune=0.75, sawtype=0|
	var osc, osc1, osc2, osc3, env, detuneCurve, centerGain, sideGain, center, freqs, side;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod] * Line.ar(Rand(0.5,1.5),1,0.02);
	freq=(freq / 2);
	amp=(amp * 0.4);
	detuneCurve = { |x|
		(10028.7312891634*x.pow(11)) -
		(50818.8652045924*x.pow(10)) +
		(111363.4808729368*x.pow(9)) -
		(138150.6761080548*x.pow(8)) +
		(106649.6679158292*x.pow(7)) -
		(53046.9642751875*x.pow(6)) +
		(17019.9518580080*x.pow(5)) -
		(3425.0836591318*x.pow(4)) +
		(404.2703938388*x.pow(3)) -
		(24.1878824391*x.pow(2)) +
		(0.6717417634*x) +
		0.0030115596
	};
	centerGain = { |x| (-0.55366 * x) + 0.99785 };
	sideGain = { |x| (-0.73764 * x.pow(2)) + (1.2841 * x) + 0.044372 };
	center = LFSaw.ar(freq, Rand());
	freqs = [
		(freq - (freq*(detuneCurve.(sawtune))*0.11002313)),
		(freq - (freq*(detuneCurve.(sawtune))*0.06288439)),
		(freq - (freq*(detuneCurve.(sawtune))*0.01952356)),
		(freq + (freq*(detuneCurve.(sawtune))*0.01991221)),
		(freq + (freq*(detuneCurve.(sawtune))*0.06216538)),
		(freq + (freq*(detuneCurve.(sawtune))*0.10745242))
	];
	side = Mix.fill(6, { |n|
		SelectX.ar(sawtype, [VarSaw.ar(freqs[n], Rand(0, 2)),LFSaw.ar(freqs[n], Rand(0, 2))], 1);
	});
	osc = (center * centerGain.(sawmix)) + (side * sideGain.(sawmix));
	osc = HPF.ar(osc, freq);
	env=EnvGen.ar(Env([0,1,0.8,0.8,0], [0.02, 0.01, sus/2, sus/2]), doneAction: 0);
	osc=(osc * env);
	osc = Mix(osc) * 1/4;
	osc = Pan2.ar(osc * amp, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "CrashServer",
	modified_by: "",
	description: "",
	category: \category,
	tags: [\tag]
	)
).add;
