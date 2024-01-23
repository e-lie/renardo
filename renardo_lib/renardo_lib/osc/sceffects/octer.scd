SynthDef.new(\octer,
{|bus, octer, octersub, octersubsub|
var osc,oct1,oct2,oct3,sub;
osc = In.ar(bus, 2);
oct1 = 2.0 * LeakDC.ar(abs(osc));
sub = LPF.ar(osc, 440);
oct2 = ToggleFF.ar(sub);
oct3 = ToggleFF.ar(oct2);
osc = SelectX.ar(octer, [osc, octer*oct1, DC.ar(0)]);
osc = osc + (octersub * oct2 * sub) + (octersubsub * oct3 * sub);
ReplaceOut.ar(bus, osc)}).add;