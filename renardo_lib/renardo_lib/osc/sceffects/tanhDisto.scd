SynthDef.new(\tanhDisto,
{|bus, tanh|
var osc;
osc = In.ar(bus, 2);
osc = osc + (osc*tanh).tanh.sqrt();
ReplaceOut.ar(bus, osc)}).add;