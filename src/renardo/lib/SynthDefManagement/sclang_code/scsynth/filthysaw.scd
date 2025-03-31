SynthDef.new(\filthysaw, {
	|bus=0, freq=0, amp=1, gate=1, fmod=0, atk=0.001, sus=1, decay=0.01, cf=100, vib=0, t_bd=0, t_sd=0, pw=0.4, pan=0|
	var base, env, osc, sd, bd;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
    base = Splay.ar(RLPF.ar(Pulse.ar(freq * [0.99, 0.5, 1.01], pw), cf.lag(0.05), 0.8).madd(SinOsc.ar(vib).range(0.5, 4)).sin);
    env = EnvGen.ar(Env.linen(atk, sus, decay), gate, doneAction:0);
	osc = Mix([base/2, (LFSaw.ar(freq)/20)]);
    bd = tanh(Ringz.ar(LPF.ar(Trig.ar(t_bd,SampleDur.ir), 2000), freq, 0.5, 5).sin*2);
    sd = tanh(Ringz.ar(LPF.ar(Trig.ar(t_sd,SampleDur.ir), 2000), freq, 0.75, PinkNoise.ar(2!2)).sin*2);
    sd = HPF.ar(sd, 60);
    osc = tanh(GVerb.ar(HPF.ar(base * env, 30), 70, 11, 0.15)*0.5 + osc + bd + sd);
	osc = osc * env * amp * 0.5;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)).add;
