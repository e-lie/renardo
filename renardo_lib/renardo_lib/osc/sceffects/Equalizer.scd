SynthDef.new(\Equalizer,
{|bus, midfreq, mid, midq, lowfreq, low, highfreq, high|
var osc;
osc = In.ar(bus, 2);
osc = BLowShelf.ar(osc, freq: lowfreq, db: low.ampdb);
osc = BPeakEQ.ar(osc, freq: midfreq, rq: midq.reciprocal, db: mid.ampdb);
osc = BHiShelf.ar(osc, freq: highfreq, db: high.ampdb);
ReplaceOut.ar(bus, osc)}).add;