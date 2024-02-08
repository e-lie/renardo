SynthDef.new(\fdist,
{|bus, fdist, fdistfreq|
var osc;
osc = In.ar(bus, 2);
osc = LPF.ar(osc, fdistfreq);
osc = (osc * 1.1 * fdist).tanh;
osc = LPF.ar(osc, fdistfreq);
osc = (osc * 1.1 * fdist).tanh;
osc = LPF.ar(osc, fdistfreq);
osc = (osc * 1.4 * fdist).tanh;
osc = LPF.ar(osc, fdistfreq);
osc = (osc * 2 * fdist).tanh;
osc = osc*0.2;
ReplaceOut.ar(bus, osc)}).add;