

# To launch once after installing or resetting reaper
initialize_reapy()

# Reaper needs to be prepared with 16 midi tracks (one per channel) before creating the instruments. To launch after reaper is completely loaded :
ensure_16_midi_tracks()

# Now you need to choose 16 reaper instruments maximum (for now) from the reaper library
# To list the instruments currently selected execute :
list_selected_reaper_instruments()


# To see all instruments in the library :
list_all_reaper_instruments()

