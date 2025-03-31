SynthDef.new(\output,
{|bus, output|
var osc;
osc = In.ar(bus, 2);
Out.ar(output, osc);
ReplaceOut.ar(bus, osc)}).add;