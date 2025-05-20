
# SCLang coding 

sccode="""
SynthDef.new(\\jjbass,
{|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
var osc, env;
sus = sus * blur;
freq = In.kr(bus, 1);
freq = [freq, freq+fmod];
freq=(freq / 1);
amp=(amp * 0.5);
osc=LFTri.ar(freq, mul: amp);
env=EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\\sin), doneAction: 0);
osc=(osc * env);
osc = Mix(osc) * 0.5;
osc = Pan2.ar(osc, pan);
ReplaceOut.ar(bus, osc)}).add;
"""
jjbass = SCInstrument(
    shortname="jjbass",
    fullname="jjbass",
    description="jjbass",
    code=sccode,
    arguments={},
    auto_load_to_server=True,
)

j1 >> jjbass()
