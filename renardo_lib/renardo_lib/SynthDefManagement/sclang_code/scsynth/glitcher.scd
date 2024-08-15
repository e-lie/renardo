SynthDef(\glitcher, {
	|bus=0, pan=0, amp=1, fmod=0, len =20, sus=1, henA=2, rate=1, henB=0.4, t=1, gate = 1|
	var osc, env,  mainEnv, speed, freq, pulse, a, bass, tone1, tone2, tone3, noise, impulse;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	env = EnvGen.ar(Env(times: [(sus * 0.25), (sus * 1)],levels: [0, amp, 0],curve: 'lin'), doneAction: 0);
	mainEnv = EnvGen.kr(Env.triangle(len,1), gate, doneAction: 0);
	speed = Array.geom(8, t, [0.75, 1.25].choose);
	freq = Array.geom(2, freq*4, 1);
	pulse = {|rat1,rat2|LFPulse.ar(rate, [0,0.5,1].choose)*LFPulse.ar(rat2)};
	a = Lag.ar(HenonN.ar(speed.choose*(mainEnv*500000.rand), henA, henB), 0.01);
	bass = SinOsc.ar(freq!2*(a*rate.rand), 1, Lag.ar(pulse.(t, speed.choose), 0.001));
	tone1 = SinOsc.ar([(freq+Rand(0,5))*a,(freq+Rand(0,5))*a], 0, 0.01*pulse.(speed.choose, speed.choose));
	tone2 = Pan2.ar(SinOsc.ar(freq.choose*a, 0, 0.1*pulse.(speed.choose, t)), a);
	tone3 = SinOsc.ar([freq.choose,freq.choose*a], 0, 0.05*pulse.(speed.choose, t))*mainEnv.round(0.25);
	noise = Pan2.ar(PinkNoise.ar(a*4*pulse.(t,t)), a);
	impulse = RLPF.ar(Impulse.ar(pulse.(t, speed.choose), a), freq.choose+(a*rate), 1, 0.1).tanh;
	osc = (bass+tone1+tone2+tone3+noise+impulse).tanh;
	osc = DelayN.ar(osc, 0.2, 0.1);
	osc = HPF.ar(osc, 200);
	osc = osc * amp * env;
	osc = Mix(osc) * 0.8;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
	},
metadata: (
	credit: "CrashServer",
	modified_by: "",
	description: "",
	category: \category,
	tags: [\tag]
	)
).add;