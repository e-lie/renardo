SynthDef.new(\tworgan, {
	|bus=0, freq=0, amp=1, fmod=0, atk=0.001, rel=0.01, pan=0, curve= -4, gate=1, bass=1, quint=1, fundamental=1, nazard=1,
	oct=1, blockFlute=1, tierce=1, larigot=1, sifflute=1, vrate=3, vdepth=0.008, vdelay=0.1, vonset=0, vrateVariation=0.1,
	vdepthVariation=0.1|
	var osc, env, vibrato;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	vibrato = Vibrato.kr(freq: freq,rate: vrate,depth: vdepth,delay: vdelay,onset: vonset, rateVariation: vrateVariation,depthVariation: vdepthVariation,);
	env = Env.linen(attackTime: atk, releaseTime: rel, curve: curve).kr(gate: gate, doneAction: 0);
	osc = DynKlang.ar(specificationsArrayRef: Ref.new([
			        [1/12,  1/7, 1, 12, 19, 24, 28, 31, 36].midiratio,
			        [bass, quint, fundamental, oct, nazard, blockFlute, tierce, larigot, sifflute].normalizeSum,nil]),freqscale: vibrato);
	osc = osc * env * amp * 0.5;
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Zé Craum",
	modified_by: "Bruno Ruviaro, Josh Mitchell, Jens Meisner",
	decription: "Tonewheel organ ",
	category: \organ,
	tags: [\tonewheelorgan, \pitched]
)).add;