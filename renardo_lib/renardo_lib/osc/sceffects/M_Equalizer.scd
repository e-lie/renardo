SynthDef.new(\M_Equalizer,
{|bus, mid, midfreq, midq|
var osc;
osc = In.ar(bus, 2);
osc = BPeakEQ.ar(osc, freq: midfreq, rq: midq.reciprocal, db: abs(mid).ampdb);
ReplaceOut.ar(bus, osc)}).add;