SynthDef.new(\linesaw, {
	// Standard values
	|bus = 0, freq = 1000, pan = 0, amp = 0.1, fmod=0, atk = 0.001, sus = 1, rel = 1.3, crv = -2,
	// lfo controls
	lforate1 = 5, lfodepth1 = 0.25, phasecenter1 = 0.35,
	lforate2 = 2.7, lfodepth2 = 0.5, phasecenter2 = 0.5,
	// Other Controls (pSwitch is 0 or 1)
	pswitch = 0, fdelay1 = 0.00025, fdelay2 = 0.00015|
	var input, lfoA, lfoB, phaseShiftA, phaseShiftB, env, saw,
	polarity, phaseA, phaseB, phase, osc;
	// Makes three lines with a slope of 1/second
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	input = Line.ar(start: 0, end: atk + sus + rel, dur: atk + sus + rel, doneAction: 0);
	input = input - [0, fdelay1, fdelay2];
	// Make two sine LFOs with freq "lfoRate" and amplitude "lfoDepth"
	lfoA = sin(2pi * (lforate1 * input).mod(1)) * lfodepth1;
	lfoB = sin(2pi * (lforate2 * input).mod(1)) * lfodepth2;
	// Use the LFOs to determine a phase parameter from 0 to 1 cycles
	phaseShiftA = (phasecenter1 + lfoA).wrap(0, 1);
	phaseShiftB = (phasecenter2 + lfoB).wrap(0, 1);
	// Make an asr envelope with a fixed sustain time
	env = (input/atk).clip(0, 1);
	env = env - ((input - (atk + sus))/rel).clip(0, 1);
	env = env.pow(exp(-1 * crv));
	// Make a sawtooth wave with freq "freq"
	saw = (input * freq).mod(1);
	polarity = 1 - (2 * pswitch);
	// Make a pulse wave from the sawtooth wave
	phaseA = sign(sign(phaseShiftA - saw) + 0.5);
	phaseA = (phaseA - 1)/2 - phaseShiftA + 0.5;
	// Add it to the saw to get a phase-shifted saw
	phaseA = saw + phaseA;
	// Rinse and repeat
	phaseB = sign(sign(phaseShiftB - saw) + 0.5);
	phaseB = (phaseB - 1)/2 - phaseShiftB + 0.5;
	phaseB = saw + phaseB;
	// Add it all together
	osc = ((polarity * (saw - 0.5)) + phaseA + phaseB)/2;
	// Filter the sound a tiny bit
	osc = (osc[0] + osc[1] + osc[2])/3 * amp;
	// Output Stuff
	osc = osc.softclip;
	osc = [osc * cos((pan + 1) * pi/4), osc * sin((pan + 1) * pi/4)];
	osc = osc * env * amp * 0.2;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "by Josh Mitchell",
	modified_by: "Jens Meisner",
	description: "",
	category: \pads,
	tags: [\pitched]
)
).add;