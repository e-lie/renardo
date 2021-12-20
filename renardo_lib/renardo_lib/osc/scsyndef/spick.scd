SynthDef.new(\spick, {
	|vib=0, bus=0, slide=0, rate=1, atk=0.1, sus=1, slidefrom=1, fmod=0, amp=1, freq=0, bits=0, pan=0|
	var osc, env;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	freq = Line.ar(freq * slidefrom, freq * (1 + slide), sus);
	freq = Vibrato.kr(freq, rate: vib);
	sus = (sus * 1.25);
	osc = (LFPulse.ar(freq).distort + Impulse.ar((freq + 1)).tan);
	env = EnvGen.ar(Env.perc(attackTime: atk, releaseTime: sus, level: 1, curve: 0), doneAction: 0);
	osc = osc * env * amp;
	osc = Mix(osc) * 0.1;
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
