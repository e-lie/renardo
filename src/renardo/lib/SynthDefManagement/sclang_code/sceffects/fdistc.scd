SynthDef.new(\fdistc,
{|bus, fdistc, fdistcfreq1, fdistcfreq2, fdistcfreq3, fdistcfreq4, fdistcm1, fdistcm2, fdistcm3, fdistcm4, fdistcq1, fdistcq2, fdistcq3, fdistcq4|
var osc;
osc = In.ar(bus, 2);
osc = RLPF.ar(osc, fdistcfreq1, fdistcq1);
osc = (osc * fdistcm1 * fdistc).tanh;
osc = RLPF.ar(osc, fdistcfreq2, fdistcq2);
osc = (osc * fdistcm2 * fdistc).tanh;
osc = RLPF.ar(osc, fdistcfreq3, fdistcq3);
osc = (osc * fdistcm3 * fdistc).tanh;
osc = RLPF.ar(osc, fdistcfreq4, fdistcq4);
osc = (osc * fdistcm4 * fdistc).tanh;
ReplaceOut.ar(bus, osc)}).add;