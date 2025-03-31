SynthDef(\lapin, {
	|bus=0, amp=1, atk=0.001, decay=0.01, sus=1,rel=0.01, level=0.8, peak=1, gate=1, pan=0, freq=0, fmod=0, vib=0, rate=1, blur=1, beat_dur=1|
	var osc, env, string;
	sus = sus*blur;
	string = { |freq|
	var delay;
	delay = freq.reciprocal;
	Pluck.ar(SinOsc.ar(Line.ar(1000, 50, 0.01)) * Env.perc(0.001, 0.01).ar, Impulse.ar(0), delay, delay, 5*rate, 0.5)};
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	osc = string.(freq) + string.(freq) + string.(freq * 0.5);
	osc = osc + (HPF.ar(LocalIn.ar(2), 3000) * -50.dbamp);
	osc = osc + HPF.ar(osc, 3000);
	osc = (osc * 32.dbamp).tanh;
	// osc = RLPF.ar(osc, 3000, 0.5);
	osc = (osc * 32.dbamp).tanh;
	osc = RLPF.ar(osc, 300, 0.5);
	osc = (osc * 32.dbamp).tanh;
	osc = CombN.ar(osc!4,4/(freq/24),4/freq,1) + osc;
	osc = BHiShelf.ar(osc, 3200, 1, -3.0);
	osc = LeakDC.ar(osc);
	osc = DelayC.ar(osc, 0.1, SinOsc.kr(0.1, [0, 1pi]).range(0, 1e-4));
	osc = HPF.ar(osc,60);
	osc = RLPFD.ar(osc,6400*[1,1.1],0.1,0.5);
	5.do {
		d = 0.2.rand;
		osc = AllpassN.ar(osc,d,d,5);
	};
	env = EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
	//osc = osc * amp * 0.35;
	osc = osc * env * amp;
	osc = Mix(osc) * 0.2;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
	},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \category,
	tags: [\tag]
	)
).add;