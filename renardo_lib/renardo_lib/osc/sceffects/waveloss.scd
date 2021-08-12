SynthDef.new(\waveloss,
{|bus, drop, dropof|
var osc;
osc = In.ar(bus, 2);
osc = WaveLoss.ar(osc, drop, outof: dropof, mode: 2);
ReplaceOut.ar(bus, osc)}).add;