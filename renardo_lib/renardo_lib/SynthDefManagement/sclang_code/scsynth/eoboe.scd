SynthDef(\eoboe,{
	|bus=0, amp=1, sus=1, dur=1, fmod=0, pan=0.0, atk=0.3, rel=0.4, rq=0.3, freq=440, range=0,
	vibrate=6, width=1, decimate=22040, decibits=2, offnote=1.005|
	var osc, osc2, env, wid;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = [freq / 2, freq / 2 * offnote];
	env = EnvGen.ar(Env.linen(atk, sus, rel, curve: \sin), doneAction:0);
	wid = LFNoise2.kr(width).range(0.001, width);
	osc = VarSaw.ar(freq + SinOsc.ar(vibrate, mul: Line.kr(0.0, 1, dur, mul:1,  doneAction: 0)), width: wid, mul:1/2);
	osc = RLPF.ar(osc, freq, rq);
	osc2 = SinOsc.ar(freq + SinOsc.ar(vibrate, mul: Line.kr(0.0, 1, dur, mul:1,  doneAction: 0)), mul:2/3);
	osc2 = RLPF.ar(osc2, freq*2, rq);
	osc = Mix([osc, osc2]);
	osc = Decimator.ar(osc, decimate, decibits);
	osc = osc * env * amp * 0.1;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Unknown",
	modified_by: "Jens Meisner",
	decription: "Distorted mock on oboe",
	category: \category,
	tags: [\tag, \tag]
)).add;