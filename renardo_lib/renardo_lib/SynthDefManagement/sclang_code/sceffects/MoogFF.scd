SynthDef.new(\MoogFF,
{|bus, mpf, mpr|
var osc;
osc = In.ar(bus, 2);
osc = MoogFF.ar(osc, mpf, mpr,0,1);
ReplaceOut.ar(bus, osc)}).add;