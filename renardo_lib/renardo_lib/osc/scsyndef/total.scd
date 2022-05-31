SynthDef.new(\total, {
	|bus = 0, amp = 0.5, fmod=0, sus=1, blur=1, rate=0, freq = 220, atk=0.25, rel = 0.08, gate=1, pan = 0|
	var osc, osc1, osc2, env;
	sus = sus * blur;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
    osc1 = SinOscFB;
	osc2 = mean(FreqShift.ar(c=osc1.ar(osc1.ar(osc1.ar(freq/b=(1..8),1),fmod/b)+b*[fmod, 99, freq], 1), 1/b)+c);
	osc = osc2 ;
	osc = osc * LinSelectX.kr(rate,[1, SinOsc.ar(4, 0, 1)]);
	env = EnvGen.ar(Env(times: [atk, sus], levels: [0, amp, 0],curve: 'lin'), doneAction: 0);
	osc = Mix(osc);
	osc = osc * env * amp * 0.4;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
	},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \organ,
	tags: [\tag]
	)
).add;