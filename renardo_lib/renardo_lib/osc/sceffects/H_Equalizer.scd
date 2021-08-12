SynthDef.new(\H_Equalizer,
{|bus, high, highfreq|
var osc;
osc = In.ar(bus, 2);
osc = BHiShelf.ar(osc, freq: highfreq, db: abs(high).ampdb);
ReplaceOut.ar(bus, osc)}).add;