SynthDef.new(\sputter, {
	//Standard Values
	|bus = 0, pan = 0, amp = 1, freq = 440, fmod = 0, atk = 0.1, sus = 1, rel = 2.5, crv = -6,
	// Modulation Controls
	pw = 0.5, noisedepth = 0.05, pwmrate = 12, pwmdepth = 0.15,
	// Resonator controls
	rstartf = 2000, rlf = 500, rrf = 5000, ratk = 0.5,
	// Other Controls (all go from 0 to 1, except for method from 0 to 4)
	method = 0, gateSwitch = 1, gateThresh = 0.5, stereoWidth = 0.75|
	var env, envNoise, resControl, pwm, osc, res;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	// Make an Envelope
	env = Env.perc(attackTime: atk, releaseTime: sus + rel, curve: crv).ar;
	// Add a Little Noise to the Envelope
	envNoise = [LFClipNoise.ar(freq: freq).range(0, noisedepth), LFClipNoise.ar(freq: freq).range(0, noisedepth)];
	envNoise = Schmidt.ar(in: env, lo: 0.0001, hi: 0.0001) * envNoise;
	env = env + envNoise;
	// Make an LFO for the Pulse Width
	pwm = LFTri.ar(freq: pwmrate, mul: pwmdepth);
	pwm = (pwm + pw).clip(0, 1);
	// Make a Square Wave
	osc = LFPulse.ar(freq: freq, width: pwm, mul: env);
	// Make a Noise Gate
	osc = osc * Schmidt.ar(in: osc, lo: gateThresh * gateSwitch, hi: gateThresh);
	//Make a Resonator for the Square
	resControl = Line.ar(start: rstartf, end: [rlf, rrf], dur: ratk);
	res = DelayC.ar(in: osc, maxdelaytime: [(1/rstartf).max(1/rlf), (1/rstartf).max(1/rrf)],
		delaytime: 1/resControl);
	// Choose how to Combine the Square and Resonator
	osc = Select.ar(
		which: method.clip(0, 4).round(1),
		array: [(osc + res).clip(0, 1),         // kinda like "snd or res"
			(osc + res).wrap(0, 1),         // kinda like "snd or res"
			osc * res,                      // kinda like "snd and res"
			(1 - osc) * res,                // kinda like "not-snd and res"
			((1 - osc) * res) + ((1 - res) * osc) // like "snd xor res"
	]);
	osc = LeakDC.ar(osc);
	// Set the Stereo Width
	osc = XFade2.ar(
		inA: [osc[1], osc[0]],
		inB: [osc[0], osc[1]],
		pan: stereoWidth
	);
	// Output Stuff
	osc = HPF.ar(in: osc, freq: freq/2);
	osc = osc * amp;
	osc = Limiter.ar(osc);
	DetectSilence.ar(in: Mix.ar(osc), doneAction: 0);
	// Stereo Version of Pan2.ar
	osc = Balance2.ar(left: osc[0], right: osc[1], pos: pan);
	osc = Mix(osc) * 0.05;
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Josh Mitchell",
	modified_by: "Jens Meisner",
	description: "",
	category: \keyboards,
	tags: [\pitched, \lead, \stereo]
	)
).add;