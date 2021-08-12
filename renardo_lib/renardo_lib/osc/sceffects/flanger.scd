SynthDef.new(\flanger,
{|bus, flanger, fdecay, flangermix|
var osc;
osc = In.ar(bus, 2);
osc = LinXFade2.ar(CombC.ar(osc, 0.01, SinOsc.ar(flanger, 0, (0.01 * 0.5) - 0.001, (0.01 * 0.5) + 0.001), fdecay, 1),  osc, 1-flangermix);
ReplaceOut.ar(bus, osc)}).add;