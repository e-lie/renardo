SynthDef.new(\sillyvoice, {
	|freq=0, amp=1, vibro=6, vibdepth=4, curve= -4, vowel=0, fmod=0, atk=0.01, sus=1, rel=0.1, lag=1, gate=1, pan=0, bus=0|
	var in, vibrato, env, va, ve, vi, vo, vu, osc;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	vibrato = SinOsc.kr(freq:vibro, mul: vibdepth);
	in = Saw.ar(Lag.kr(freq, lag) + vibrato);
	env = Env.linen(atk, sus, rel, curve: -4).kr(doneAction: 0);
	va = BBandPass.ar(in: in,freq: [ 600, 1040, 2250, 2450, 2750 ],
		bw: [ 0.1, 0.067307692307692, 0.048888888888889, 0.048979591836735, 0.047272727272727 ],
		mul: [ 1, 0.44668359215096, 0.35481338923358, 0.35481338923358, 0.1 ]);
	ve = BBandPass.ar(in: in,freq: [ 400, 1620, 2400, 2800, 3100 ] ,
		bw: [ 0.1, 0.049382716049383, 0.041666666666667, 0.042857142857143, 0.038709677419355 ],
		mul: [ 1, 0.25118864315096, 0.35481338923358, 0.25118864315096, 0.12589254117942 ]);
	vi = BBandPass.ar(in: in,freq: [ 250, 1750, 2600, 3050, 3340 ] ,
		bw: [ 0.24, 0.051428571428571, 0.038461538461538, 0.039344262295082, 0.035928143712575 ],
		mul: [ 1, 0.031622776601684, 0.15848931924611, 0.079432823472428, 0.03981071705535 ] );
	vo = BBandPass.ar(in: in,freq:[ 400, 750, 2400, 2600, 2900 ] ,
		bw: [ 0.1, 0.10666666666667, 0.041666666666667, 0.046153846153846, 0.041379310344828 ],
		mul: [ 1, 0.28183829312645, 0.089125093813375, 0.1, 0.01 ]);
	vu = BBandPass.ar(in: in,freq: [ 350, 600, 2400, 2675, 2950 ],
		bw: [ 0.11428571428571, 0.13333333333333, 0.041666666666667, 0.044859813084112, 0.040677966101695 ],
		mul: [ 1, 0.1, 0.025118864315096, 0.03981071705535, 0.015848931924611 ]);
	osc = SelectX.ar(Lag.kr(vowel,lag),[va, ve, vi, vo, vu]);
	osc = Mix.new(osc) * 2;
	osc = osc * env * amp;
	osc = Pan2.ar(osc,pan);
	ReplaceOut.ar(bus,osc)
},
metadata: (
	credit: "Bruno Ruviaro",
	modified_by: "Jens Meisner",
	description: "",
	category: \choir,
	tags: [\voice, \bass]
	)
).add;
