# Tutorial 22: Using REAPER Backend (Fresh / OSC extension)

# This tutorial uses the new REAPER backend based on a native Rust OSC extension.
# It does NOT require reapy or the old Lua ReaScript bridge.

# ── Step 1 : Install REAPER ────────────────────────────────────────────────────
# Install a recent version of REAPER (https://www.reaper.fm)
# Launch it at least once so that it creates its config directory.

# ── Step 2 : Install the Renardo REAPER extension ─────────────────────────────
# This downloads the pre-built Rust extension from the Renardo GitHub release
# and installs it in REAPER's UserPlugins directory.
# Run this once (or again with force=True to update):

setup_reaper_fresh()

# If the download fails you can pass a specific release tag:
# setup_reaper_fresh(tag="v0.8.0")
# Force reinstall:
# setup_reaper_fresh(force=True)

# After installation, RESTART REAPER to load the extension.

# ── Step 3 : Enable REAPER backend in Renardo ──────────────────────────────────
# In the Renardo webclient, go to the "Audio Backends" tab and enable REAPER,
# or set REAPER_BACKEND_ENABLED = true in your settings.toml.

# ── Step 4 : Prepare your REAPER project ──────────────────────────────────────
# Open REAPER and create tracks for your instruments.
# MIDI tracks will be driven by Renardo via MIDI.
# Audio tracks (no MIDI input) can also be scanned but will receive no MIDI.
#
# Example tracks you could create:
#   "Bass Synth"  → load a bass VST instrument
#   "Lead"        → load a lead VST instrument
#   "Drums"       → load a drum VST instrument
#   "Pad"         → load a pad VST instrument

# ── Step 5 : Scan the project and create instrument facades ───────────────────
# With REAPER running and the extension loaded, execute:

reaper_instruments = create_reaper_instruments(max_midi_tracks=16, scan_audio_tracks=True)

# This scans all tracks and returns a dict {snake_track_name: facade, '_project': project}
# Track "Bass Synth" becomes reaper_instruments["bass_synth"]
# Track "Lead"       becomes reaper_instruments["lead"]
# Track "Drums"      becomes reaper_instruments["drums"]

# You can also create facades manually for a specific track:
# from renardo.reaper_backend_fresh import ReaperFreshInstrumentFacade
# bass = ReaperFreshInstrumentFacade(reaper_instruments["_project"], "Bass Synth", midi_channel=1)

# ── Step 6 : Play ─────────────────────────────────────────────────────────────
# Use the .out attribute of each facade as the SynthDef for a Player:

b1 >> reaper_instruments["bass_synth"].out([0, 3, 5, 7], dur=0.5)

b1 >> reaper_instruments["bass_synth"].out([0, 3, 5], dur=[0.75, 0.75, 0.5])

p1 >> reaper_instruments["lead"].out([0, 2, 4, 7], dur=1/4)

d1 >> reaper_instruments["drums"].out([0, 2, 4], dur=1)

# Volume (linear fader, 0.0–1.5, where ~0.716 ≈ 0 dB):
b1 >> reaper_instruments["bass_synth"].out([0, 3, 5], vol=0.6)

# ── Step 7 : Latency handling ─────────────────────────────────────────────────
# REAPER introduces a MIDI latency compared to the SuperCollider backend.
# Adjust Clock.latency and Clock.midi_nudge to align both backends:

Clock.latency = 0.5      # add latency to SuperCollider notes
Clock.midi_nudge = -0.16 # nudge MIDI notes earlier

# Test alignment by running a SC instrument and a REAPER instrument in parallel:
b1 >> blip()
b2 >> reaper_instruments["bass_synth"].out([0, 3, 5])

# ── Cleanup ───────────────────────────────────────────────────────────────────
Clock.clear()
