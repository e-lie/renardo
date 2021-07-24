SynthDef.new(\squish, {
	|amp=1, dur=1, sus=1, pan=0, freq=0, fmod=0, bus=0, blur=1, rate=0, beat_dur=1, atk=0.01, rel=0.01, peak=1, level=0.8, xlatk=0.1, xlsus=0.01, xldur=1, xlmul=0.1, pulserate=4, pulsewidth=0.5|
	var osc, env;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = (freq / 2);
	osc = Ringz.ar(Pulse.ar(pulserate, pulsewidth), freq, sus, amp + (pulserate / 10));
	osc = osc * XLine.ar(xlatk, xlsus, xldur, xlmul, doneAction: 0);
	osc = osc.cos;
	env = Env.linen(attackTime: atk, sustainTime: sus, releaseTime: rel).kr(doneAction: 0);
	osc = osc * env * amp;
	osc = Mix(osc) * 0.15;
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
