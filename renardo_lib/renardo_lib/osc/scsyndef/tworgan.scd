SynthDef.new(\tworgan, {
	|bus=0, freq=0, amp=1, fmod=0, atk=0.001, sus=1, rel=0.01, pan=0, curve= -4, gate=1, bass=1, qnt=1, fndmtl=1, nazard=1,
	oct=5, bflute=1, trc=1, lrigot=1, sflute=1, vrate=3, vdepth=0.008, vdelay=0.1, vonset=0, vratevar=0.1, vdepthvar=0.1|
	var osc, env, vibrato;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	amp = amp / 4;
	vibrato = Vibrato.kr(freq: freq,rate: vrate,depth: vdepth,delay: vdelay, onset: vonset, rateVariation: vratevar,depthVariation: vdepthvar,);
	env = Env.linen(attackTime: atk, sustainTime: sus, releaseTime: rel, curve: curve).kr(gate: gate, doneAction: 0);
	osc = DynKlang.ar(specificationsArrayRef: Ref.new([
			        [1/12,  1/7, 1, 12, 19, 24, 28, 31, 36].midiratio,
			        [bass, qnt, fndmtl, oct, nazard, bflute, trc, lrigot, sflute].normalizeSum,nil]), freqscale: vibrato);
	osc = osc * env * amp * 0.3;
	osc = Pan2.ar(osc, pan);
	ReplaceOut.ar(bus, osc)
},
metadata: (
	credit: "Zé Craum",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	decription: "Tonewheel organ ",
	category: \organ,
	tags: [\tonewheelorgan, \pitched]
)).add;