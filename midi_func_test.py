midi = MidiIn(1)
midimap = midi.load_midimap(0)
valmap = midi.load_valmap("/home/bbscar/Projects/Music/Renardo_Dev/src/MidiMax_ValMap_Set.json")

midi.run()

midi.print_message(True)

midi.print_message(False)

midi.midimaps()

print(midimap)

valmap = midi.load_valmap("/home/bbscar/Projects/Music/Renardo_Dev/src/MidiMax_ValMap.json")

valmap = midi.load_valmap("/home/bbscar/Projects/Music/Renardo_Dev/src/MidiMax_ValMap_Set.json")

print(valmap)

midi.save_valmap("/home/bbscar/Projects/Music/Renardo_Dev/src/MidiMax_ValMap_Set.json")

# Set values of first unit
midi.set_value("U0:E0", "s1.lpf", [800, 20, 0])
midi.set_value("U0:E1", "s1.lpr", [1/8, 1, 1])
midi.set_value("U0:E2", "s1.drive", [1/2, 1, 3/4])

# Set values of first unit in second slot
midi.set_value("U0:E0", "s1.hpf", [200, 8000, 0])
midi.set_value("U0:E1", "s1.hpr", [1, 1/8, 1])

# Set values of first unit in third slot
midi.set_value("U0:E0", "s1.shape", [0, 2, 0])
midi.set_value("U0:E1", "s1.formnat", [0, 4, 0])

midi.del_value("U0:E1", "s1.formnat")

# Set values of second unit
midi.set_value("U1:E0", "s1.room", [1/3, 1, 0])
midi.set_value("U1:E1", "s1.mix", [1/4, 3/4, 0])
midi.set_value("U1:E2", "s1.verb", [1/3, 1, 0])

# Set value of unit group counter
midi.set_value("U0:E4", "Group", ["U0:E0", "U0:E1", "U0:E2"])
midi.set_value("U1:E4", "Group", ["U1:E0", "U1:E1", "U1:E2"])
midi.set_value("U2:E4", "Group", ["U2:E0", "U2:E1", "U2:E2"])
midi.set_value("U3:E4", "Group", ["U3:E0", "U3:E1", "U3:E2"])
midi.set_value("U4:E4", "Group", ["U4:E0", "U4:E1", "U4:E2"])
midi.set_value("U5:E4", "Group", ["U5:E0", "U5:E1", "U5:E2"])
midi.set_value("U6:E4", "Group", ["U6:E0", "U6:E1", "U6:E2"])
midi.set_value("U7:E4", "Group", ["U7:E0", "U7:E1", "U7:E2"])
# Set value of unit group element value memory 
midi.set_value("U0:E5", "Group", ["U0:E0", "U0:E1", "U0:E2"])
midi.set_value("U1:E5", "Group", ["U1:E0", "U1:E1", "U1:E2"])
midi.set_value("U2:E5", "Group", ["U2:E0", "U2:E1", "U2:E2"])
midi.set_value("U3:E5", "Group", ["U3:E0", "U3:E1", "U3:E2"])
midi.set_value("U4:E5", "Group", ["U4:E0", "U4:E1", "U4:E2"])
midi.set_value("U5:E5", "Group", ["U5:E0", "U5:E1", "U5:E2"])
midi.set_value("U6:E5", "Group", ["U6:E0", "U6:E1", "U6:E2"])
midi.set_value("U7:E5", "Group", ["U7:E0", "U7:E1", "U7:E2"])

# Set value of first unit group push button
midi.set_value("U0:E3", "beat1.amp", [1, 0])

# Set value of first unit group fader
midi.set_value("U0:E5", "Group", ["U0:E0", "U0:E1", "U0:E2"])

# Set value of unit 8 switch button
midi.set_value("U8:E3", "s1.amp", [0, 1])

midi.get_value("U0:E5")

midi.run()

midi.stop()

midi.close()

s1 >> dbass([0, 2], dur=PDur(3,5)); b1 >> play("V", dur=2, amplify=1/8, amp=1).stop()

s1.amp=1

s1.stop()

b1 >> play("V", dur=1/2, amplify=1/2, amp=0)
b2 >> play("-", dur=1/8, amp=0)
beat1 = Group(b1,b2)


# ---------------------------------------------------------------------

midi2 = MidiIn(2)

midi2.print_message(True)
