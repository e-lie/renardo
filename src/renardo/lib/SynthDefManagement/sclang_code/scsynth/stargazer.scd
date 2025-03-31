SynthDef.new(\stargazer, {
	|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.0001, decay=0.01, rel=0.01, peak=1, level=0.8, wave=0, sub=0, detune=1, mix=(-1.0), freq1=880, freq2=880, res1=0.0, res2=0.0,	rate1 = 10, rate2 = 10, rate3 = 10, depth1 = 1, depth2 = 1, depth3 = 1, alias=44100, redux=24, lfo1type1 = 0, 	lfo1type2 = 0, 	lfo1type3 = 0|
	var osc, env, detuned, pitch, lfo1, lfo2, lfo3, filter1, filter2;
	freq = In.kr(bus, 1);
	freq = [freq, freq+fmod];
	~wt = Array.fill(90, {
		var numSegs = rrand (90, 20);
	Env(
		(({rrand(0.0, 1.0)}!(numSegs-1))*[1, -1]).scramble,
		{rrand(1, 20)}!numSegs,
		'sine'
		// {rrand(-20,20)}!numSegs
	).asSignal(1024).asWavetable;
		});
	~vbuf = Buffer.allocConsecutive(90, s, 2048);
	~vbuf.do({
		arg buf, i;
		buf.loadCollection(~wt[i]);
	});
	lfo1=Select.kr(lfo1type1, [LFTri.kr(rate1), LFSaw.kr(rate1), LFPulse.kr(rate1)]);
	lfo2=Select.kr(lfo1type2, [LFTri.kr(rate2), LFSaw.kr(rate2), LFPulse.kr(rate2)]);
	lfo3=Select.kr(lfo1type3, [LFTri.kr(rate3), LFSaw.kr(rate3), LFPulse.kr(rate3)]);
	detuned = Select.ar(sub, [VOsc.ar(wave, freq*detune.midiratio), VOsc.ar(wave, (freq*0.5)*detune.midiratio)]);
	wave = ~vbuf[0].bufnum + wave;
	env = EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\sin), doneAction: 0);
	osc = VOsc.ar(wave, freq);
	osc = XFade2.ar(osc, detuned, mix);
	filter1 = MoogLadder.ar(osc, freq1*lfo1.range(1, depth1), res1);
	osc = Decimator.ar(filter1, alias, redux);
	filter2 = MoogLadder.ar(osc, freq2*lfo2.range(1, depth2), res2);
	osc = Splay.ar(filter2);
	osc = LeakDC.ar(osc);
	osc = osc * amp * env * lfo3.range(1, depth3);
	osc = Limiter.ar(osc, 0.1);
	ReplaceOut.ar(bus, osc)
	},
metadata: (
	credit: "CrashServer",
	modified_by: "Jens Meisner",
	description: "",
	category: \organ,
	tags: [\tag]
	)
).add;
