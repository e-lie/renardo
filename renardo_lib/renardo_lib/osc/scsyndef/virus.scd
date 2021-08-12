SynthDef(\virus, {
	arg len = 2, freq = 420, fmod = 0.1, vib = 0.25, rate = 1, atk=0.01, sus=1, rel=0.09, prate1=1, prate2=2, gate = 1, bus=0, amp=1, pan=0;
	var mainEnv, speed, freqs, pulse, a, bass, tone1, tone2, tone3, noise, impulse, osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	mainEnv = EnvGen.kr(Env.triangle(len,1), gate, doneAction:0);
	speed = Array.geom(4, rate, [1.75, 1.25].choose);
	freqs = Array.geom(8, freq/2, 1.5);
	pulse = {|prate1, prate2|LFPulse.ar(prate1, [0,0.5,1].choose)*LFPulse.ar(prate2)};
	a = Lag.ar(HenonN.ar(speed.choose*(mainEnv*10000.rand), fmod, vib), 0.01);
	bass = SinOsc.ar(freqs!2*(a*1.0.rand), 0, Lag.ar(pulse.(rate, speed.choose), 0.001));
	tone1 = SinOsc.ar([(freqs+Rand(0,5))*a,(freqs+Rand(0,5))*a], 0, 0.01*pulse.(speed.choose, speed.choose));
	tone2 = Pan2.ar(SinOsc.ar(freqs.choose*a, 0, 0.1*pulse.(speed.choose, rate)), a);
	tone3 = SinOsc.ar([freqs.choose,freqs.choose*a], 0, 0.05 * pulse.(speed.choose, rate))*mainEnv.round(0.25);
	noise = Pan2.ar(PinkNoise.ar(a*0.1*pulse.(rate,rate)), a);
	impulse = RLPF.ar(Impulse.ar(pulse.(rate, speed.choose), a), freqs.choose+(a*10), 0.01, 0.1).tanh;
	osc = (bass+tone1+tone2+tone3+noise+impulse).tanh;
	env = EnvGen.ar(Env.asr(atk, sus, rel, curve:\lin), doneAction: 0);
	osc = Mix.ar(osc);
	osc = osc * amp * env * 0.8;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc);
	},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \noise,
	tags: [\tag]
	)
).add;
