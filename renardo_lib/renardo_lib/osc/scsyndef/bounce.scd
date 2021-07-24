SynthDef.new(\bounce, {
	arg bus=0, gate=1, atk=0.1, sus=1, rel=0.09, amp=1, pan=0, freq=0, fmod=0, para1=2, para2=2.5, nharm=3;
	var env, osc;
	freq = In.kr(bus, 1);
	freq = [freq,freq+fmod];
	osc = CombN.ar(Decay2.ar(Impulse.ar([[para1,para2], 1]), 0.08, sus), delaytime:0) * Blip.ar(freq, nharm);
	env = Env.linen(atk,sus,rel, curve:\lin).kr(doneAction:0);
	osc = Mix(osc) * 0.1;
	osc = osc * env * amp;
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
