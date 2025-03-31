SynthDef.new(\DFM1,
{|bus, dfm, dfmr, dfmd|
var osc;
osc = In.ar(bus, 2);
osc = DFM1.ar(osc, dfm, dfmr, dfmd,0.0);
ReplaceOut.ar(bus, osc)}).add;