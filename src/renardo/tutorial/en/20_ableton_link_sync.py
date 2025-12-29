# Tutorial 20: Ableton Link Synchronization

# Ableton Link is a protocol that allows you to synchronize tempo and phase
# across multiple music applications and devices on the same network.

# Enable Ableton Link synchronization
Clock.sync_to_link(enabled=True)

# Disable Ableton Link
Clock.sync_to_link(enabled=False)

# Check Link status (shows tempo, beat, phase, connected peers, etc.)
Clock.link_status()

# Example
Clock.sync_to_link(enabled=True)
Clock.bpm = 140
Clock.meter = (4, 4)

d1 >> play("x-o-", dur=1)
b1 >> bass([0, 0, 3, 5], dur=0.5)
p1 >> pluck(P[0, 2, 4, 7].amen(), dur=1/4)

# If your beats are slightly offset from Link beats, adjust the phase offset
# Default is 0.5, but you may need to adjust based on your setup
Clock.link_phase_offset = 0.5   # Half beat forward
Clock.link_phase_offset = 0.0   # No offset
Clock.link_phase_offset = -0.5  # Half beat backward

# Adjust the BPM (this will be synchronized across all Link-enabled apps)
Clock.bpm = 120

# Change the time signature (affects quantum alignment)
# For 3/4 time:
Clock.meter = (3, 4)

# To stop Link sync
Clock.sync_to_link(enabled=False)

# You can also manually set the quantum if needed:
Clock.link_quantum = 4  # Force 4-beat alignment regardless of meter

# To use automatic quantum based on meter again:
Clock.link_quantum = None



# Control how often to resynchronize with Link (in beats)
# Lower values = tighter sync but more CPU, higher values = looser but efficient
Clock.link_sync_interval = 1   # Resync every beat (default)
Clock.link_sync_interval = 4   # Resync every 4 beats (one bar in 4/4)

# === PRACTICAL EXAMPLE ===

# 1. Start Ableton Live (or any Link-enabled app)
# 2. Enable Link in that app
# 3. Enable Link in Renardo
Clock.sync_to_link(enabled=True)

# 4. Check status to see if connected
Clock.link_status()
# You should see "Peers: 1" (or more if multiple apps are connected)

# 5. Play something
p1 >> pluck([0, 2, 4, 7], dur=1)

# 6. The tempo will be synchronized with Ableton Live
# Try changing tempo in either app - they stay in sync!

# 7. Launch clips in Ableton - they will be in phase with Renardo

# === TROUBLESHOOTING ===

# If beats are not aligned:
# - Check Clock.link_status() to see current phase
# - Adjust Clock.link_phase_offset in increments of 0.25
# - Common values: -0.5, 0.0, 0.5, 1.0

# If tempo is drifting:
# - Decrease Clock.link_sync_interval for tighter sync
# - Check that both apps are on the same network

# If no peers are detected:
# - Make sure Link is enabled in other apps
# - Check firewall settings (Link uses UDP port 20808)
# - Ensure all devices are on the same local network

# === ADVANCED USAGE ===

# Link works great with live performance setups:
# - Sync Renardo with Ableton Live for hybrid performances
# - Connect multiple Renardo instances across computers
# - Sync with iOS apps like Audiobus, AUM, etc.

# Link synchronization happens in real-time with very low latency
# The dual-threaded clock architecture ensures precise timing


