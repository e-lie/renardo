SynthDef.new(\feeddelay,
{|bus, feed, feedfreq|
var osc,out;
osc = In.ar(bus, 2);
out = osc + Fb({		arg feedback;		osc = CombN.ar(HPF.ar(feedback*feed, feedfreq) + osc, 0.5, 0.25).tanh;	},0.5,0.125);
ReplaceOut.ar(bus, osc)}).add;