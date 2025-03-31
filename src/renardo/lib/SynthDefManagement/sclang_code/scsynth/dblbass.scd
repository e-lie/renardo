SynthDef.new(\dblbass, {
	|bus = 0, amp = 1, freq = 440, fmod=0, atk = 0.01, sus=0, rel = 1.0, crv = \lin, vel = 1.0,
	// Other Controls
	freqdev = 4, op1mul = 0.1, op2mul = 0.1, op3mul = 0.1, spread = 0.5, subAmp = 0.1, pan=0|
	var env, op1, op2, op3, op4, osc, sub;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = (freq / 4);
	env = Env.linen(attackTime: atk, sustainTime: sus, releaseTime: rel, curve: crv).kr(doneAction: 0);
	op1 = SinOsc.ar(freq: freq * 4, mul: vel / 2 + op1mul);
	op2 = SinOsc.ar(freq: freq * 3, phase: op1, mul: vel / 2 + op2mul);
	op3 = SinOsc.ar(freq: freq * 2, phase: op2, mul: vel / 2 + op3mul);
	op4 = SinOsc.ar(freq: freq + NRand(-1 * freqdev, freqdev, 3), phase: op3, mul: amp * 0.5);
	osc = {DelayN.ar(in: op4, maxdelaytime: 0.06, delaytime: Rand(0.03, 0.06))} !8;
	osc = LeakDC.ar(osc);
	osc = Splay.ar(inArray: osc, spread: spread, level: 0.6, center: pan);
	sub = SinOsc.ar(freq: freq/2, mul: env * subAmp);
	sub = Pan2.ar(sub, pan);
	osc = osc + sub * env;
	osc = Limiter.ar(osc);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Matias Monteagudo",
	modified_by: "Suhel Keswani, Josh Mitchell, Jens Meisner",
	description: "",
	category: \bass,
	tags: [\pitched, \bass]
)).add;