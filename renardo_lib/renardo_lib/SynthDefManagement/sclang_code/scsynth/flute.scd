SynthDef(\flute, {
	|bus=0, scl = 0.4, freq = 440, fmod=0, atk=0.1, dur=1, sus=1, ipress = 0.9, ibreath = 0.09, ifeedbk1 = 0.4, ifeedbk2 = 0.4, gate = 1, pan = 0, amp = 1|
	var kenv1, kenv2, kenvibr, kvibr, sr, cr, block, poly, osc, ifqc, fdbckArray;
	var aflow1, asum1, asum2, afqc, atemp1, ax, apoly, asum3, avalue, atemp2, aflute1;
	sr = SampleRate.ir;
	cr = ControlRate.ir;
	block = cr.reciprocal;
	freq = In.kr(bus, 1);
	ifqc = freq;
	// noise envelope
	kenv1 = EnvGen.kr(Env.linen(atk, sus*2/3, sus*1/3, 1.0, \lin), doneAction: 0);
	// overall envelope
	kenv2 = EnvGen.kr(Env.linen(atk, sus*2/3, sus*1/3, 1.0, \sin), doneAction: 0);
	// vibrato envelope
	kenvibr = EnvGen.kr(Env.linen(atk, sus*2/3, sus*1/3, 1.0, \sin), doneAction:0);
	// create air flow and vibrato
	aflow1 = LFClipNoise.ar(sr, kenv1);
	kvibr = SinOsc.ar(5, 0, 0.1 * kenvibr);
	asum1 = (ibreath * aflow1) + kenv1 + kvibr;
	afqc = ifqc.reciprocal - (asum1/20000) - (9/sr) + (ifqc/12000000) - block;
	fdbckArray = LocalIn.ar(1);
	aflute1 = fdbckArray;
	asum2 = asum1 + (aflute1 * ifeedbk1);
	//ax = DelayL.ar( asum2, ifqc.reciprocal * 0.5, afqc * 0.5 );
	ax = DelayC.ar(asum2, ifqc.reciprocal - block, afqc * 0.5 - (asum1/ifqc/cr) + 0.001);
	apoly = ax - (ax.cubed);
	asum3 = apoly + (aflute1 * ifeedbk2);
	avalue = LPF.ar(asum3, 2100);
	aflute1 = DelayC.ar(avalue, ifqc.reciprocal - block * 4, afqc);
	fdbckArray = [aflute1];
	LocalOut.ar(fdbckArray);
	osc = avalue * 1/2;
	osc = osc * kenv2 * amp * 0.15;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc);
},
metadata: (
	credit: "John E. Bower",
	modified_by: "Jens Meisner",
	description: "",
	category: \flute,
	tags: [\slideflute, \wind, \bassflute]
)).add;