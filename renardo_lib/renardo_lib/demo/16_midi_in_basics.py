# Initialize Midi function
midi = MidiIn()
# Check on available midi devices
print(midi.available_ports)


# Lets start with the added Midi functionalities. Ok, check what devices are available. First is usually system default, Second is in my case MidiMixer

# Midi function init again with midi device
midi = MidiIn(1)

# Check in Tools >> Midimaps, or with this command to dedicate needed Midi map
midi.midimaps()

# Check MidiMaps via command line or in menu

# Load Midi map
midimap = midi.load_midimap(0)

# Display MidiMap json file as dictionary in console
print(midimap)

# As you can see the first in the json dictionary is the name of each element. In the following list are all specifications
# given in MidiMapper >> Type, CC, Value Range

# Load Value map
valmap = midi.load_valmap("/path/to/valmap.json")

# Display Valmap json file as dictionary in console
print(valmap)

# Here you can see the ValMap. It is similar to MidiMap in its structure. Name of element. A list with its value range behind followed by an empty dictionary. # The value map has depth layers for counters, buttons that switches between database of settings...attributes of groups, synths and/or samples. The default of # layers is 3...however, you can change it with the line below.

# In case you want to change the depth of layer used with a count element,
# change it when loading ValMap by adding the layer number at the end >> Default: 3
valmap = midi.load_valmap("/path/to/valmap.json", 3)

# There is an example of an element with 3 attributes in 3 layers

# Next shows the way to add those attributes and its values

# Set values of first unit
midi.set_value("U0:E0", "s1.lpf", [450, 80, 1])
midi.set_value("U0:E1", "s1.lpr", [1/8, 1, 1])
midi.set_value("U0:E2", "s1.drive", [3/4, 2, 3/4])

# Name first, Attribute of synth, group, or sample next, last a list of minimum, maximum and default value

# Check values added to a particular element
midi.get_value("U0:E0")

# Set values of first unit in second slot
midi.set_value("U0:E0", "s1.hpf", [200, 8000, 0])
midi.set_value("U0:E1", "s1.hpr", [1, 1/8, 1])

# Check values added to a particular element
midi.get_value("U0:E0")

# Set values of first unit in third slot
midi.set_value("U0:E0", "s1.shape", [0, 2, 0])
midi.set_value("U0:E1", "s1.formnat", [0, 4, 0])

# Oh sh..., I wrote formnat instead of formant

midi.get_value("U0:E1")

# If a value with wrong naming is added, just remove it
midi.del_value("U0:E1", "s1.formnat")

# And add it again
midi.set_value("U0:E1", "s1.formant", [0, 4, 0])

midi.get_value("U0:E1")

# Set values of second unit
midi.set_value("U1:E0", "s1.room", [1/3, 1, 0])
midi.set_value("U1:E1", "s1.mix", [1/4, 3/4, 0])
midi.set_value("U1:E2", "s1.verb", [1/3, 1, 0])

# Set value of unit group count button element
midi.set_value("U0:E4", "Group", ["U0:E0", "U0:E1", "U0:E2"])
midi.set_value("U1:E4", "Group", ["U1:E0", "U1:E1", "U1:E2"])


# Set value of unit group fader element
midi.set_value("U0:E5", "Group", ["U0:E0", "U0:E1", "U0:E2"])
midi.set_value("U1:E5", "Group", ["U1:E0", "U1:E1", "U1:E2"])

# Set value of first unit group switch button
midi.set_value("U0:E3", "s1.amp", [1, 0])

# Set value of second unit group switch button to mute beat
midi.set_value("U1:E3", "beat1.amp", [1, 0])

# Set value of first unit group fader
midi.set_value("U0:E5", "Group", ["U0:E0", "U0:E1", "U0:E2"])

# In case of a group fader you call the fader or knob "Group" in its value argument. Then you add all element names to the
# list in order to get all adressed. This will be according to the attributes under the count number you set it up for.

# Check again, how the template changed
print(valmap)

# Save modified template file to reload it, whenever you use this device with your composition
midi.save_valmap("/path/to/valmap.json")

# Load a ValMap
valmap = midi.load_valmap("/path/to/valmap.json")

# The midi functionality is set to work with all gui environment (well, that it what it suppose to do, please comment)

# Start listening to Midi input and execute value changes and/or events
midi.run()

# Try assign attributes of s1 or synth1
s1 >> dbass([0, 2], dur=PDur(3,5), amplify=2/3, amp=1)

# Add a beat to it, which can be switch on/off
b1 >> play("V", dur=1, amplify=1/8, amp=1)
b2 >> play("-", dur=1/2, echo=[0, 1/4], amp=1)
b3 >> play("o", dur=2, delay=1, amplify=1/4, amp=1)
b4 >> play("s", dur=1, delay=1/2, amplify=1/2, amp=1)
beat1 = Group(b1,b2,b3,b4)

# Stop listening to Midi input messages
midi.stop()

# Close MidiIn()
midi.close()


# -------------------------------------------------------------------
