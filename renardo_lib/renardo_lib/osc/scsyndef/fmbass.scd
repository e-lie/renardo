SynthDef.new(\fmbass, {
	//Standard Values
	|bus = 0, pan = 0, amp = 0.1, freq = 150, fmod = 0, atk = 0.1, sus=1, rel = 1, crv = -4,
	// Other Controls
	atkFraction = 0.05, relFraction = 0.7, modIndex = 80, modRatio = 1.51,
	subAmp = 0.99, modFB = 1|
	var scale, mAtk, mRel, modulatorEnv, modulator, carrierEnv, carrier, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	// Scale the att/rel for the Modulator
	scale = (atkFraction + relFraction);
	scale = Select.kr(which: InRange.kr(in: scale, lo: 1, hi: inf), array: [
			DC.kr([atkFraction, relFraction]),
			DC.kr([atkFraction/scale, relFraction/scale])
	]);
	scale = scale * (atk + sus + rel);
	mAtk = scale[0];
	mRel = scale[1];
	// Modulator
	modulatorEnv = Env.perc(attackTime: mAtk, releaseTime: mRel, level: modIndex, curve: crv).ar;
	modulator = SinOscFB.ar(freq: freq * modRatio, feedback: modFB, mul: modulatorEnv);
	// Carrier
	carrierEnv = Env.perc(attackTime: atk, releaseTime: sus + rel, curve: crv).ar(doneAction: 0);
	carrier = SinOsc.ar(freq: freq + modulator, mul: carrierEnv);
    // Add a Sub
	osc = carrier + SinOsc.ar(freq: freq/2, mul: carrierEnv * subAmp);
	// Output Stuff
	osc = Limiter.ar(osc);
	osc = Mix(osc);
	osc = osc * amp * 0.2;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Josh Mitchell",
	modified_by: "Jens Meisner",
	description: "FM-based SynthDef mostly from Eli Fieldsteel",
	category: \bass,
	tags: [\pitched, \fm]
)).add;