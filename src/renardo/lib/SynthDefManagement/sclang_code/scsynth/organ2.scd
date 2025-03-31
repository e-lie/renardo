SynthDef.new(\organ2, {
	|bus = 0, freq = 0, fmod=0, pan = 0, sus = 1, amp = 1, gate = 1|
    var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
    osc = Splay.ar(SinOsc.ar(freq*Array.geom(4,1,2), mul:1/8));
    osc = osc + SinOsc.ar(freq/2, mul:0.2)!2;
    env = EnvGen.ar(Env.linen(0.001,sus,0.01), gate, doneAction:0);
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
