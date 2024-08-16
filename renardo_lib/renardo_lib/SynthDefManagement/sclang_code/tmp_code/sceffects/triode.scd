SynthDef.new(\triode,
{|bus, triode|
var osc,sc;
osc = In.ar(bus, 2);
sc = triode * 10 + 1e-3;
osc = (osc * (osc > 0)) + (tanh(osc * sc) / sc * (osc < 0));
osc = LeakDC.ar(osc)*1.2;
ReplaceOut.ar(bus, osc)}).add;