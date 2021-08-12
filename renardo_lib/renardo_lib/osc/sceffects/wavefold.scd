SynthDef.new(\wavefold,
{|bus, fold, symetry, smooth|
var osc,gain,compensationGain,envFollower,ampgain;
osc = In.ar(bus, 2);
compensationGain = max(LinLin.kr(fold, 0, 1, 1, 20) * 0.75, 1).reciprocal;
envFollower = EnvFollow.ar((osc * 2).softclip, 0.9999);
ampgain = (compensationGain * (1 - 0.4)) + (envFollower * 0.4);
osc = SmoothFoldS.ar((osc + LinLin.kr(symetry, 0, 1, 1, 0)) * LinLin.kr(fold, 0, 1, 1, 20), smoothAmount: smooth);
osc = LeakDC.ar(osc*ampgain);
ReplaceOut.ar(bus, osc)}).add;