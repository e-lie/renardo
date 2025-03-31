SynthDef.new(\lofi,
{|bus, lofi, lofiwow, lofiamp|
var osc,minWowRate,wowRate,maxDepth,maxLfoDepth,depth,depthLfoAmount,wowMul,maxDelay,ratio,threshold,gain;
osc = In.ar(bus, 2);
osc = HPF.ar(osc, 25);
ratio = LinExp.kr(lofiamp, 0, 1, 0.15, 0.01);
threshold = LinLin.kr(lofiamp, 0, 1, 0.8, 0.33);
gain = 1/(((1.0-threshold) * ratio) + threshold);
osc = Limiter.ar(Compander.ar(osc, osc, threshold, 1.0, ratio, 0.1, 1, gain), dur: 0.0008);
minWowRate = 0.5;
wowRate = LinExp.kr(lofiwow, 0, 1, minWowRate, 4);
maxDepth = 35;
maxLfoDepth = 5;
depth = LinExp.kr(lofiwow, 0, 1, 1, maxDepth - maxLfoDepth);
depthLfoAmount = LinLin.kr(lofiwow, 0, 1, 1, maxLfoDepth).floor;
depth = LFPar.kr(depthLfoAmount * 0.1, mul: depthLfoAmount, add: depth);
wowMul = ((2 ** (depth * 1200.reciprocal)) - 1)/(4 * wowRate);
maxDelay = (((2 ** (maxDepth * 1200.reciprocal)) - 1)/(4 * minWowRate)) * 2.5;
osc = DelayC.ar(osc, maxDelay, SinOsc.ar(wowRate, 2, wowMul, wowMul + ControlRate.ir.reciprocal));
osc = ((osc * LinExp.kr(lofiamp, 0, 1, 1, 2.5))).tanh;
osc = LPF.ar(osc, LinExp.kr(lofi, 0, 1, 2500, 10000));
osc = HPF.ar(osc, LinExp.kr(lofi, 0, 1, 40, 1690));
osc = MoogFF.ar(osc, LinExp.kr(lofi, 0, 1, 1000, 10000), 0);
ReplaceOut.ar(bus, osc)}).add;