SynthDef.new(\octafuz,
{|bus, octafuz, octamix|
var osc,dis,osc_base;
osc = In.ar(bus, 2);
osc_base = osc;
dis = [1,1.01,2,2.02,4.5,6.01,7.501];
dis = dis ++ (dis*6);
osc = ((osc * dis*octafuz).sum.distort);
osc = (osc * 1/16)!2;
osc = LinXFade2.ar(osc_base, osc, octamix);
ReplaceOut.ar(bus, osc)}).add;