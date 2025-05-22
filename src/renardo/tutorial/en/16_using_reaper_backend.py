# Part one - Install and configure Reaper

# First install a recent Reaper DAW version (use normal version not portable version)

# We need to configure python connection to Reaper with reapy library.
# This first part is still a bit dark magic glitchy because REAPER does not collaborate well for external control... stabilisation in progress

# In renardo Go to "Audio Backends" tab REAPER and click "Initialize REAPER Integration"
# Read and follow the steps carefully (waiting for reaper start or close before clicking continue).
# If you miss a step, close Reaper and restart the process by clicking the button.

# To test the working integration execute in code editor

import reapy
print(reapy.Project()) # output should be something like : Project("(ReaProject*)0x0000000005FD88A0")

# See "troubleshooting Reaper Integration / reapy" in the documentation, if you cannot get this simply working.

# Part two - Install base open source plugins ( Classic plugin configuration )

# Install vital synth (https://vital.audio) and Surge XT (https://surge-synthesizer.github.io/) VST3 version
# 
# Check in Reaper the Preferences > VST section. If scan for plugins does not detect your plugins :
# on Windows and MacOS default plugin install should work directly,
# On linux beware that plugin may be installed in /usr/lib/vst3 which is not scanned by REAPER by default
# => you can launch the following command line to be sure : ln -s /usr/lib/vst3 ~/.vst3/global
# Generally you should adjust the list of "VST plugins Paths" so REAPER find the vst3 in the right directory

# Part three - Configure MIDI connection

# Reaper needs to be prepared with 16 midi tracks (one per channel) before creating the instruments. Execute the following after reaper is completely loaded :
ensure_16_midi_tracks() # Midi tracks should appear in Reaper interface.

# Enable one MIDI input in Reaper in Preference > MIDI Inputs

# Launch Renardo SuperCollider backend with MIDI, either automatically 
# with the Audio Backends > SuperCollider features of Renardo or manually in SuperCollider.

# Depending of your OS you need to configure MIDI connection between SuperCollider and REAPER (tutorial for that soon :)
# Then you can test the connection by adding a plugin instrument in "chan1" track and executing :

m1 >> MidiOut(channel=0)

# Part four - Using the integration with Reaper Instrument

# Now you need to choose 16 reaper instruments maximum (for now) from the reaper library
# To list the instruments currently selected execute :
list_selected_reaper_instruments()

# To see all instruments in the library :
list_all_reaper_instruments()

# Select instrument names in a list with
set_selected_instruments(["bass303", "lonesine", "gone", "solar2", "pluckbass"])

# To create and add to reaper the selected instruments execute
create_selected_instruments()

# test an instrument
b1 >> pluckbass([0,0,0,2], dur=[.75,.75,.5])

# to troubleshoot if this does not work
# Be sure Renardo.midi is started, the MIDI messages are correctly sent from SuperCollider to Reaper
# Look for errors in the terminal log of Renardo
# Troubleshooting documentation page (Work in progress)

# Part five - Latency handling

# To synchronize notes from SuperCollider backends and Reaper backends...
# We can add latency to SuperCollider backend with 

Clock.latency = 0.5

# Then we can adjust negative midi nudge with 

Clock.midi_nudge = -0.16

# Launch two instrument Reaper and SuperCollider to adjuste the value for your machine

b1 >> blip()

b2 >> pluckbass()

