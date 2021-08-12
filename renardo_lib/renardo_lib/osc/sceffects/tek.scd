SynthDef.new(\tek,
{|bus, tek, tekr, tekd|
var osc,osc_low,osc_med,osc_high,osc_base,lfo;
osc = In.ar(bus, 2);
lfo = SinOsc.ar(0.5, phase: 0, mul: 50, add: 800);
osc = In.ar(bus, 2);
osc_base = osc;
osc_low = LPF.ar(osc, lfo) * 1;
osc_med = BPF.ar(osc, lfo * 2);
osc_med = osc_med + Ringz.ar(CrossoverDistortion.ar(osc_med, 1, 0.1, 0.4),100, decaytime: 0.15, mul:0.1);
osc_med = LeakDC.ar(osc_med);
osc_high = HPF.ar(osc, 4000 + SinOsc.ar(4, mul: 24));
osc = osc_low + osc_med + osc_high;
osc = DFM1.ar(osc, [400, 600], 0.99, tekd, 0) + osc;
osc = RHPF.ar(Gammatone.ar(osc, tekr), tekr, mul:2) + osc;
osc = LinXFade2.ar(osc_base, osc, tek);
ReplaceOut.ar(bus, osc)}).add;