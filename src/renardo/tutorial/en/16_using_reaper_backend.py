

# To launch once after installing or resetting reaper
initialize_reapy()

# Reaper needs to be prepared with 16 midi tracks (one per channel) before creating the instruments. To launch after reaper is completely loaded :
ensure_16_midi_tracks()

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
# check if Renardo.midi is started, the MIDI messages are correctly sent from SuperCollider to Reaper
# Look for errors in the terminal log of Renardo