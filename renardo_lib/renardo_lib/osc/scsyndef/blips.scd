SynthDef.new(\blips, {
	|bus = 0, freq = 0, numharm = 20, fmod=0, atk = 0.1, rel = 1, sus=1, amp = 1, pan = 0, beatsPercent = 1.001|
	var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = Env.perc(atk, rel * sus * 20, amp).kr(doneAction: 0);
	osc = LeakDC.ar(Mix(Blip.ar([freq, freq*beatsPercent], numharm)));
	osc = osc * env * amp / 1.5;
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;