SynthDef.new(\dubdelay,
{|bus, dubd, dublen, dubwidth, dubfeed|
var osc,dry;
osc = In.ar(bus, 2);
dry = osc;
osc = osc + Fb({ |feedback| var left, right; var magic = LeakDC.ar(feedback*dubfeed + osc); magic = HPF.ar(magic, 400); magic = LPF.ar(magic, 5000); magic = magic.tanh; #left, right = magic; magic = [DelayC.ar(left, 1, LFNoise2.ar(12).range(0,dubwidth)), DelayC.ar(right, 1, LFNoise2.ar(12).range(dubwidth,0))].reverse;	},dublen);
osc = SelectX.ar(dubd, [dry, osc]);
ReplaceOut.ar(bus, osc)}).add;