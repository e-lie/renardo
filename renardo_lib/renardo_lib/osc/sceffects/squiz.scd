SynthDef.new(\squiz,
{|bus, squiz|
var osc;
osc = In.ar(bus, 2);
osc = Squiz.ar(osc, squiz);
ReplaceOut.ar(bus, osc)}).add;