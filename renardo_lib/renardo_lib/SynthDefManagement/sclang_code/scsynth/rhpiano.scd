SynthDef.new(\rhpiano, {
    |bus=0, freq=0, pan=0, amp=1, fmod=0, atk=0.001, sus=1, vel=0.8, modindex=0.2, mix=0.2, lfospeed=0.4, lfodepth=0.1|
    var env1, env2, env3, env4, osc1, osc2, osc3, osc4, osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
    lfospeed = lfospeed * 12;
	env = Env.linen(atk, sus, 0.04, curve: -4).kr(doneAction: 0);
    env1 = EnvGen.ar(Env.adsr(0.001, 1.25, 0.0, 0.04, curve: \lin));
    env2 = EnvGen.ar(Env.adsr(0.001, 1.00, 0.0, 0.04, curve: \lin));
    env3 = EnvGen.ar(Env.adsr(0.001, 1.50, 0.0, 0.04, curve: \lin));
    env4 = EnvGen.ar(Env.adsr(0.001, 1.50, 0.0, 0.04, curve: \lin));
    osc4 = SinOsc.ar(freq * 0.5) * 2pi * 2 * 0.535887 * modindex * env4 * vel;
    osc3 = SinOsc.ar(freq, osc4) * env3 * vel;
    osc2 = SinOsc.ar(freq * 15) * 2pi * 0.108819 * env2 * vel;
    osc1 = SinOsc.ar(freq, osc2) * env1 * vel;
	osc = Mix((osc3 * (1 - mix)) + (osc1 * mix)) * 0.3;
	osc = osc * (SinOsc.ar(lfospeed) * lfodepth + 1);
	osc = osc * env * amp * 0.3;
    osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
