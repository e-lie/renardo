SynthDef.new(\SLPF,
{|bus, spf, spr, spfslide, spfend|
var osc,spfenv;
osc = In.ar(bus, 2);
spfenv = EnvGen.ar(Env.new([spf, spfend], [spfslide]));
osc = RLPF.ar(osc, spfenv, spr);
ReplaceOut.ar(bus, osc)}).add;