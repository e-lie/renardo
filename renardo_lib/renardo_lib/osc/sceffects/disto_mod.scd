SynthDef.new(\disto_mod,
{|bus, disto, smooth, distomix|
var osc;
osc = In.ar(bus, 2);
osc = LinXFade2.ar(CrossoverDistortion.ar(osc, amp:0.5*disto, smooth:smooth),  osc, 1-distomix);
ReplaceOut.ar(bus, osc)}).add;