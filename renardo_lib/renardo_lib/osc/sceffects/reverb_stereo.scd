SynthDef.new(\reverb_stereo,
{|bus, room2, mix2, damp2, revatk, revsus|
var osc,dry;
osc = In.ar(bus, 2);
dry = osc;
osc = HPF.ar(osc, 100);
osc = LPF.ar(osc, 10000);
osc = FreeVerb2.ar(osc[0], osc[1], 1, room2, damp2);
osc = osc * EnvGen.ar(Env([0,1,0], [revatk,revsus], curve: 'welch'));
osc = SelectX.ar(mix2, [dry, osc]);
ReplaceOut.ar(bus, osc)}).add;