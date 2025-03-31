SynthDef.new(\rlead, {
	|bus = 0, freq=0, amp=1, fmod=0, gate=1, atk=0.01, sus=1, bps=2, seqnote1=3, seqnote2=1, seqnote3=2, pan = 0|
    var osc, env, seq;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
    seq = Demand.kr(Impulse.kr(bps*4), 0, Dseq(freq*[seqnote1,seqnote2,seqnote3], inf)).lag(0.02);
    osc = LFSaw.ar(freq*{rrand(0.995, 1.005)}!2);
    osc = Splay.ar(osc, 2, center:pan);
    osc = MoogFF.ar(osc, seq, 2);
	env = Env.linen(atk, sus, 0.01, curve:-4).kr(doneAction:0);
    osc = osc * env * amp * 0.4;
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
