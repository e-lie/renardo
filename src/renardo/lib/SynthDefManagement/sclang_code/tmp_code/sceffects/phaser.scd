SynthDef.new(\phaser,
{|bus, phaser, phaserdepth|
var osc,delayedSignal;
osc = In.ar(bus, 2);
delayedSignal = osc;
for(1, 4, {|i| delayedSignal = AllpassL.ar(delayedSignal, 0.01 * 4.reciprocal, LFPar.kr(LinExp.kr(phaser, 0, 1, 0.275, 16), i + 0.5.rand, LinExp.kr(phaserdepth*4.reciprocal, 0, 1, 0.0005, 0.01 * 0.5), LinExp.kr(phaserdepth*4.reciprocal, 0, 1, 0.0005, 0.01 * 0.5)), 0)});
osc = osc + delayedSignal;
ReplaceOut.ar(bus, osc)}).add;