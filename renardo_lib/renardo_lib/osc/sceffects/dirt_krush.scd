SynthDef.new(\dirt_krush,
{|bus, krush, kutoff|
var osc,signal,freq;
osc = In.ar(bus, 2);
freq = Select.kr(kutoff > 0, [DC.kr(4000), kutoff]);
signal = (osc.squared + (krush * osc)) / (osc.squared + (osc.abs * (krush-1.0)) + 1.0);
signal = RLPF.ar(signal, clip(freq, 20, 10000), 1);
osc = SelectX.ar(krush * 2.0, [osc, signal]);
ReplaceOut.ar(bus, osc)}).add;