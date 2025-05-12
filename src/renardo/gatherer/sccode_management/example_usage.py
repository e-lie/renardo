# Example global_config.py
"""
Define global defaults for all banks, synths, and effects.
"""
global_defaults = {
    "amp": 0.5,
    "pan": 0.0,
    "out": 0,
}

# Example bank_config.py in a specific bank directory
"""
Define default arguments for this specific bank.
"""
default_arguments = {
    "amp": 0.7,  # Override global default
    "attack": 0.01,
    "release": 0.1,
}

# Example synth definition (bass/simple_bass.py)
"""
Define a simple bass synth.
"""
from renardo.gatherer.sccode_management.sc_resource import SCInstrument

# SuperCollider code for the synth definition
sc_code = '''
SynthDef("simple_bass", { |out=0, freq=60, cutoff=1000, resonance=0.5, 
                          attack=0.05, decay=0.3, sustain=0.7, release=0.5, amp=0.5, pan=0|
    var sig, env;
    env = EnvGen.kr(Env.adsr(attack, decay, sustain, release), doneAction: 2);
    sig = Saw.ar(freq) + SinOsc.ar(freq/2, 0, 0.5);
    sig = RLPF.ar(sig, cutoff, resonance);
    sig = sig * env * amp;
    sig = Pan2.ar(sig, pan);
    Out.ar(out, sig);
}).add;
'''

synth = SCInstrument(
    shortname="simple_bass",
    fullname="Simple Bass Synthesizer",
    description="A basic subtractive bass synth with low-pass filter",
    code=sc_code,
    arguments={
        "freq": 60,
        "cutoff": 1000,
        "resonance": 0.5,
        "attack": 0.05,
        "decay": 0.3,
        "sustain": 0.7,
        "release": 0.5,
    }
)

# Example effect definition (reverb/plate_reverb.py)
"""
Define a plate reverb effect.
"""
from renardo.gatherer.sccode_management.sc_resource import SCEffect

# SuperCollider code for the effect
sc_code = '''
SynthDef("plate_reverb", { |in, out=0, mix=0.5, room_size=0.7, damp=0.5, freeze=0.0, amp=1.0|
    var dry, wet;
    dry = In.ar(in, 2);
    wet = JPverb.ar(
        dry,
        t60: room_size * 10,
        damp: damp,
        freeze: freeze
    );
    Out.ar(out, XFade2.ar(dry, wet, mix * 2 - 1) * amp);
}).add;
'''

effect = SCEffect(
    shortname="plate_reverb",
    fullname="Plate Reverb",
    description="A plate reverb simulation",
    code=sc_code,
    arguments={
        "mix": 0.5,
        "room_size": 0.7,
        "damp": 0.5,
        "freeze": 0.0,
    }
)

# Example usage
from pathlib import Path
from renardo.gatherer.sccode_management.sccode_library import SCCodeLibrary
from renardo.lib.music_resource import ResourceType

# Load the entire library
library = SCCodeLibrary(Path("/path/to/library"))

# Get a specific synth
synth = library.get_resource(0, ResourceType.INSTRUMENT, "bass", "simple_bass")
if synth:
    print(f"Loaded synth: {synth.fullname}")
    print(f"Description: {synth.description}")
    print(f"Arguments: {synth.arguments}")
    print("SuperCollider code:")
    print(synth.code)
    
    # Generate code with custom parameters
    custom_code = synth.get_code_with_args(freq=100, cutoff=2000, attack=0.1)
    print("\nCustomized SuperCollider code:")
    print(custom_code)

# Get a specific effect
effect = library.get_resource(0, ResourceType.EFFECT, "reverb", "plate_reverb")
if effect:
    print(f"Loaded effect: {effect.fullname}")
    print(f"Description: {effect.description}")
    print(f"Arguments: {effect.arguments}")
    print("SuperCollider code:")
    print(effect.code)

# Search for resources containing "bass"
print("\nSearching for 'bass':")
bass_resources = library.find_resources("bass")
for resource in bass_resources:
    print(f"{resource['bank']} > {resource['section']} > {resource['category']} > {resource['shortname']}")
    print(f"  {resource['description']}")

# Get all resources in a category
bank = library.get_bank(0)
if bank:
    bass_category = bank.get_category(ResourceType.INSTRUMENT, "bass")
    if bass_category:
        print("\nAll bass instruments:")
        for details in bass_category.get_resource_details():
            print(f"{details['shortname']} - {details['fullname']}")
            print(f"  Arguments: {', '.join(details['arguments'])}")