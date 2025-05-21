
# When you tell some player to play an instrument like...
b1 >> jbass(degree=[0,5,2], dur=.75)

# ... the jbass part is in Renardo an object called an Instrument
# Here we will be looking at SCInstrument which the Instrument type proposed by the SuperCollider backend of Renardo (ReaperInstrument will be handled pretty be differently)
# Lets say we would like to create a new bass (copy of FoxDot jbass for the example).
# We can define directly a new SuperCollider synthdef in a multiline string and use it to create a SCInstrument instance like this :

jjbass = SCInstrument(shortname="jjbass",code="""
SynthDef.new(\\jjbass,
{|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
var osc, env;
sus = sus * blur;
freq = In.kr(bus, 1);
freq = [freq, freq+fmod];
freq=(freq / 4);
amp=(amp * 0.5);
osc=LFTri.ar(freq, mul: amp);
env=EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\\sin), doneAction: 0);
osc=(osc * env);
osc = Mix(osc) * 0.5;
osc = Pan2.ar(osc, pan);
ReplaceOut.ar(bus, osc)}).add;
""")

b1 >> jjbass(degree=[0,5,2], dur=.75)

# ...or like this :

sccode = """
SynthDef.new(\\jjbass,
{|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
var osc, env;
sus = sus * blur;
freq = In.kr(bus, 1);
freq = [freq, freq+fmod];
freq=(freq / 4);
amp=(amp * 0.5);
osc=LFTri.ar(freq, mul: amp);
env=EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\\sin), doneAction: 0);
osc=(osc * env);
osc = Mix(osc) * 0.5;
osc = Pan2.ar(osc, pan);
ReplaceOut.ar(bus, osc)}).add;
"""
jjbass = SCInstrument(shortname="jjbass",code=sccode)

# SCInstruments can be live edited and will be loaded each time into supercollider server
# For example, while letting the b1 player play, change freq=(freq / 4) by freq=(freq / 2) in the preceding code and evaluate
# The pitch should now be up an octave

# If this looks hard to understand for you, don't worry ! SuperCollider language (SCLang) is not easy to approach...
# A proper tutorial for understanding the basis of SuperCollider synthesis should come soon here :)

# But not let's look at something crucial for Renardo customization : default values for arguments !
# SCInstrument objects have an "arguments" field where you can define the default values used by SCIntrument when nothing is given

jjbass.arguments={"dur":.5}

b1 >> jjbass(degree=[0,5,2]) # no given dur here so will use dur=.5

# You can also use that for predefined SCInstrument and this is also valid for effects parameters

blip.arguments={"dur":.25, "lpf":2000}
b1 >> blip()

# to reset you can
blip.arguments={}

# You can use this in your startup file to start a music coding session with prepared/customized instruments
# ... but ideally don't forget to show us your customizations startup if you play publicly to support open/reproducible music

# SCInstruments are the default, historical instruments inherited from FoxDot where there were called SynthDefProxies. The legacy FoxDot mechanism of defining SynthDef synthesis using custom python/SCLang binding as been removed in favor of a more direct SCLang writing, easier to maintain and customize.

# To go further you can have a look at the folder sccode_library inside you user directory (see user directory section of th settings)
# There you can also customize the instruments and effects from Renardo and soon upload them to the community asset collections server https://collections.renardo.org