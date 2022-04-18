SynthDef(\ecello,{
	|bus=0, amp=1, sus=1, dur=1, fmod=0, pan=0.0, atk=0.3, rel=0.09, rq=0.9, freq=440, range=0,
	vibrate=6, width=1, decimate=22040, decibits=4, offnote=1.005|
	var osc, osc2, env, w;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = freq / 4;
	env = EnvGen.ar(Env.linen(atk, sus, rel, curve: \lin), doneAction: 0);
	w = LFNoise2.kr(width).range(0.001, 0.8);
	osc = VarSaw.ar([freq, freq * offnote] + SinOsc.ar(vibrate, mul: Line.kr(0.0, 1, dur, mul: 1, doneAction: 0)), width: w, mul: 1);
	osc = RLPF.ar(osc, freq, rq);
	osc2 = SyncSaw.ar(freq + SinOsc.ar(vibrate, mul: 1), mul: 1/2);
	osc2 = RLPF.ar(osc2, freq, rq);
	osc = Mix.ar([osc, osc2]);
	osc = Decimator.ar(osc, decimate, decibits);
	osc = osc * env * amp * 0.3;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Unknown",
	modified_by: "Jens Meisner",
	decription: "Bird singer",
	category: \category,
	tags: [\tag, \tag]
)).add;