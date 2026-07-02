sccode = """
SynthDef.new(\\output,
{|bus, output|
var osc;
osc = In.ar(bus, 2);
Out.ar(output, osc);
ReplaceOut.ar(bus, osc)}).add;
"""

effect = SCEffect(
    shortname="output",
    fullname="output",
    description="Output effect",
    code=sccode,
    arguments={
        "output": 0
    },
    order=2,
)
