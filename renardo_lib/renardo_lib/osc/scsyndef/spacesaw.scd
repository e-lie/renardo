SynthDef.new(\spacesaw, {
	// Standard Values
	|bus = 0, amp = 1, gate = 1, freq = 100, fmod=0, pan = 0, atk = 0.25, sus=1, rel = 0.3, crv = -4,
	// Filter and Distortion Controls
	filterLo = 100, filterHi = 2000, rq = 0.3, sidePreamp = 2, midPreamp = 1,
	// Chorus and Mid/Side Controls (balance is 0 to 1 and monoSwitch is 0 or 1)
	lfoFreq = 0.1, lfoDepth = 0.015, balance = 0.5, monoSwitch = 0|
	var env, lfo, leftIn, rightIn, mid, side, leftOut, rightOut, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	// Envelope and LFO
	env = EnvGen.ar(Env.linen(atk, sus, rel, (sus / 2),curve: crv), doneAction: 0);
	lfo = SinOsc.ar(freq: lfoFreq, phase: [0, pi]);
	lfo = lfo.range(1 - lfoDepth, 1 + lfoDepth);
	//Stereo signal with beatings
	leftIn = LFSaw.ar(freq: freq * lfo[0]);
	rightIn = LFSaw.ar(freq: freq * lfo[1]);
	// L/R to M/S conversion
	mid = (leftIn + rightIn)/2;
	side = (leftIn - rightIn)/2;
	// FX on the M/S signal
	mid = RLPF.ar(in: mid, freq: LinExp.ar( in: env, srclo: 0, srchi: 1, dstlo: filterLo, dsthi: filterHi),
		rq: rq, mul: midPreamp);
	mid = mid.softclip/midPreamp.softclip;
	mid = mid * (1 - balance).clip(0, 1) * env;
	side = RLPF.ar(in: side, freq: LinExp.ar(in: env, srclo: 0, srchi: 1, dstlo: filterHi, dsthi: filterLo),
		rq: rq, mul: sidePreamp);
	side = side.softclip/sidePreamp.softclip;
	side = side * balance.clip(0, 1) * env;
	// Output Stuff and Converting Back to L/R
	leftOut = mid + side;
	rightOut = mid - side;
	osc = Select.ar(which: monoSwitch, array: [[leftOut, rightOut], Pan2.ar(leftOut, pan)]);
	osc = osc * amp * 1/2;
	osc = Limiter.ar(osc);
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Josh Mitchell",
	modified_by: "Jens Meisner",
	description: "",
	category: \pads,
	tags: [\pitched, \midsidesaw]
	)
).add;
