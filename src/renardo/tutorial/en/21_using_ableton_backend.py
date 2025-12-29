# Tutorial 21: Using Ableton Live Backend

# 1. Install Ableton Live 11 or above
# 2. Install the pylive dependencies (should be installed with Renardo)
# 3. Install AbletonOSC Remote Script in Ableton Live
#    Download from: https://github.com/ideoforms/AbletonOSC

# To install AbletonOSC Remote Script (see github README of pylive and abletonOSC for up to date info)
# 1. Download and extract the repository as a zip file
# 2. Rename the folder from "AbletonOSC-master" to "AbletonOSC"
# 3. Copy the folder to the Remote Scripts directory:
#    - Windows: C:\Users\[username]\Documents\Ableton\User Library\Remote Scripts
#    - macOS: /Users/[username]/Music/Ableton/User Library/Remote Scripts
# 4. Restart Ableton Live
# 5. In Ableton: Preferences > Link / Tempo / MIDI
#    - Select "AbletonOSC" from the Control Surface dropdown
# 6. You should see: "AbletonOSC: Listening for OSC on port 11000"

# Enable Ableton Backend
# ABLETON_BACKEND_ENABLED=true dans le fichier toml de settings ou via l'interface du webclient

# Make sure Ableton Live is running with AbletonOSC device loaded
# Then create the Ableton instruments in Renardo

# This will:
# - Connect to Ableton Live via OSC
# - Scan all tracks, devices, and parameters
# - Create instrument facades for each of the first 16 tracks for easy access

ableton_instruments = create_ableton_instruments(max_midi_tracks=16, scan_audio_tracks=True)


# Example: If you have a track named "Bass Synth" in Ableton:
b1 >> mybass([0, 3, 5, 7], dur=0.5) # mybass is the name of the track in ableton in snake case

# If you have a track named "Lead":
p1 >> thelead([0, 2, 4, 7], dur=1/4)

# If you have a track named "Drums":
d1 >> drumkiit([0,2,4], dur=1)

b1 >> mybass([0, 3, 5], cutoff=2000)

b1 >> bass_synth([0, 3, 5], cutoff=linvar([500, 4000], 8))

b1 >> bass_synth([0, 3, 5], vol=0.8)

b1 >> bass_synth([0, 3, 5], pan=0.5)

# These ableton parameters DON'T work with patterns only timevars
# (for structural reason pattern are only possible through SuperCollider)

# Clock.bpm changes ableton bpm and link clock bpm (see ableton link synchronisation)

Clock.clear()
