SynthDef.new(\L_Equalizer,
{|bus, low, lowfreq|
var osc;
osc = In.ar(bus, 2);
osc = BLowShelf.ar(osc, freq: lowfreq, db: abs(low).ampdb);
ReplaceOut.ar(bus, osc)}).add;