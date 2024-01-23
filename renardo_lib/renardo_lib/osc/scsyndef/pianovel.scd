(
SynthDef(\pianovel,
	{|bus=0, freq=440, fmod=0, gate=1, amp=0.5, velocity=80, hard=0.8, sus=1, blur=1, velhard=0.6, pan=0, vib=0|
	var env;
	var son = MdaPiano.ar([freq + fmod], gate, release: 0.9, stereo: 0.8, sustain: sus * blur, vel: velocity, hard: hard, velhard: velhard);
	son = TwoPole.ar(son, 200,0.5, mul:0.5) + son/2;
	env=EnvGen.ar(Env(times: [sus],levels: [(amp * 1), (amp * 1)],curve: 'step'), doneAction: 0);
	son = (son * env);
	DetectSilence.ar(son, 0.01, doneAction:2);
	ReplaceOut.ar(bus, Splay.ar(son * amp, 1, 1, pan));
}).add;
)
