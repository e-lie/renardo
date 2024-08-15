SynthDef.new(\fmrhodes, {
	|bus = 0, freq = 0, gate = 1, pan = 0, amp = 1, fmod=0, vel = 0.8, modindex = 0.2, oscmix = 0.1, lfospeed = 0.4, lfodepth = 0.1|
    var env1, env2, env3, env4, osc1, osc2, osc3, osc4, env, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
    lfospeed = lfospeed * 12;
    env1 = EnvGen.ar(Env.adsr(0.001, 1.25, 0.0, 0.04, curve: \lin));
    env2 = EnvGen.ar(Env.adsr(0.001, 1.00, 0.0, 0.04, curve: \lin));
    env3 = EnvGen.ar(Env.adsr(0.001, 1.50, 0.0, 0.04, curve: \lin));
    env4 = EnvGen.ar(Env.adsr(0.001, 1.50, 0.0, 0.04, curve: \lin));
    osc4 = SinOsc.ar(freq * 0.5) * 2pi * 2 * 0.535887 * modindex * env4 * vel;
    osc3 = SinOsc.ar(freq, osc4) * env3 * vel;
    osc2 = SinOsc.ar(freq * 9) * 2pi * 0.108819 * env2 * vel;
    osc1 = SinOsc.ar(freq, osc2) * env1 * vel;
    osc = Mix((osc3 * (1 - oscmix)) + (osc1 * oscmix)) * 0.08;
    osc = osc * (SinOsc.ar(lfospeed) * lfodepth + 1);
    env = EnvGen.ar(Env.asr(0, 1, 0.1), gate, doneAction: 0);
	osc = osc * env * amp;
    osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "unknown",
	modified_by: "Josh Mitchell, Bruno Ruviaro, Jens Meisner",
	decription: "FM Rhodes Synthesizer. Native SuperCollider port of STK's Rhodey",
	category: \keyboards,
	tags: [\fmSynth, \tag]
)).add;