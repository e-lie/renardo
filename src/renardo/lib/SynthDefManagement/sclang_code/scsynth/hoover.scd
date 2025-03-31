SynthDef.new(\hoover, {
	|bus=0, freq=0, amp=1, pan=0, fmod=0, atk=0.01, sus=1, rel=0.09, offnote=0.5|
    var osc, bw, delay, decay, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
    bw = 1.035;
    osc = { DelayN.ar(Saw.ar(freq * ExpRand(bw, 1 / bw)) + Saw.ar(freq * offnote * ExpRand(bw, 1 / bw)), 0.01, Rand(0, 0.01)) }.dup(18);
    osc = (Splay.ar(osc)).atan;
    env = Env.linen(atk, sus, rel, curve: \lin).kr(doneAction: 0);
	osc = Mix(osc * env) * amp * 0.1;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
