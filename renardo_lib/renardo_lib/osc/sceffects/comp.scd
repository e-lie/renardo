SynthDef.new(\comp,
{|bus, comp, comp_above, comp_below|
var osc;
osc = In.ar(bus, 2);
osc = Compander.ar(osc, osc, thresh: comp, slopeAbove: comp_above, slopeBelow: comp_below, clampTime: 0.01, relaxTime: 0.01, mul: 1);
ReplaceOut.ar(bus, osc)}).add;