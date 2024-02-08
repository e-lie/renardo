SynthDef.new(\sample_atk,
{|bus, sample_atk, sample_sus|
var osc,env;
osc = In.ar(bus, 2);
env = EnvGen.ar(Env.new(levels: [0,1,0], times:[sample_atk, sample_sus], curve: 'lin'));
osc = osc*env;
ReplaceOut.ar(bus, osc)}).add;