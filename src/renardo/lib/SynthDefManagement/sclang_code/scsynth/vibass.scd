SynthDef.new(\vibass, {
	|freq=0, amp=1, bus=0, pan=0, fmod=0, atk=0.01, sus=1, dur=1, rel=0.3, curve = -9,
	vibrate=9|
	var env, osc, osc1, osc2;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = freq / 2;
	env = Env.linen(atk, sus, rel, curve:curve).kr(doneAction: 0);
	osc1 = SinOsc.ar(freq);
	osc2 = SinOsc.ar(Line.kr(freq + vibrate, freq, dur, doneAction:0));
	osc = Mix([osc1, osc2]);
	osc = osc * env * amp * 0.15;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add
