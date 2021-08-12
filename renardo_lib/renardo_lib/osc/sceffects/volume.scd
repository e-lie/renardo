SynthDef.new(\volume,
{|bus, vol|
var osc;
osc = In.ar(bus, 2);
osc = osc*vol;
ReplaceOut.ar(bus, osc)}).add;