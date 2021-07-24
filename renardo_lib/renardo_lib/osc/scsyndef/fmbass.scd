SynthDef.new(\fmbass, {
	//Standard Values
	|bus = 0, pan = 0, amp = 0.1, freq = 440, fmod = 0, atk = 0.1, sus=1, rel = 1, crv = -4,
	// Other Controls
	atkfract = 0.05, relfract = 0.7, modindex = 80, modratio = 1.51,
	subamp = 0.99, modfb = 1|
	var scale, mAtk, mRel, modulatorEnv, modulator, carrierEnv, carrier, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	// Scale the att/rel for the Modulator
	scale = (atkfract + relfract);
	scale = Select.kr(which: InRange.kr(in: scale, lo: 1, hi: inf), array: [
			DC.kr([atkfract, relfract]),
			DC.kr([atkfract/scale, relfract/scale])
	]);
	scale = scale * (atk + sus + rel);
	mAtk = scale[0];
	mRel = scale[1];
	// Modulator
	modulatorEnv = Env.perc(attackTime: mAtk, releaseTime: mRel, level: modindex, curve: crv).ar;
	modulator = SinOscFB.ar(freq: freq * modratio, feedback: modfb, mul: modulatorEnv);
	// Carrier
	carrierEnv = Env.perc(attackTime: atk, releaseTime: sus + rel, curve: crv).ar(doneAction: 0);
	carrier = SinOsc.ar(freq: freq + modulator, mul: carrierEnv);
    // Add a Sub
	osc = carrier + SinOsc.ar(freq: freq/2, mul: carrierEnv * subamp);
	// Output Stuff
	osc = Limiter.ar(osc);
	osc = Mix(osc) * amp * 0.2;
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