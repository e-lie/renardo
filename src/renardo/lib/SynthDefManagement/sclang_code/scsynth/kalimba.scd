SynthDef.new(\kalimba, {
	|bus=0, freq=0, amp=1, pan=0, atk=0.01, sus=1, fmod=0, rel=0.7, oscmix=0.4, relMin=2.5, relMax=3.5|
	var osc, env1, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	rel = Rand(relMin, relMax);
	osc = SinOsc.ar(freq);
	env1 = EnvGen.ar(Env.perc(atk, rel,curve:-4), doneAction: 0);
	osc = osc * env1 * 1/2;
	osc = (osc * (1 - oscmix)) + (DynKlank.ar(`[
		[240*ExpRand(0.9, 1.1),
		2020*ExpRand(0.9, 1.1),
		3151*ExpRand(0.9, 1.1)],
		[-7, 0, 3].dbamp,
		[0.8, 0.05, 0.07]],
	PinkNoise.ar * EnvGen.ar(Env.perc(atk, 0.01))) * oscmix);
	env = Env.linen(atk, sus, rel, curve:\sin).kr(doneAction:0);
	osc = osc * env * amp * 0.15;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Nathan Ho aka Snappizz",
	modified_by: "Josh Mitchell, Bruno Ruviaro, Jens Meisner",
	description: "",
	category: \percussion,
	tags: [\pitched, \kalimba]
)
).add;
