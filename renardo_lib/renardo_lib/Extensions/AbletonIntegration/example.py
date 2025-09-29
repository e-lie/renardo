"""
Example usage of AbletonIntegration

Prerequisites:
1. Ableton Live must be running
2. AbletonOSC must be installed and loaded as a Control Surface
   (Download from: https://github.com/ideoforms/AbletonOSC)
3. pylive must be installed: pip install pylive

Setup your Live set:
- Create MIDI tracks with instruments
- Name tracks descriptively (e.g., "Bass", "Lead Synth", "Drums")
- The first 16 MIDI tracks will be scanned automatically
"""

from renardo_lib.Extensions.AbletonIntegration import create_ableton_instruments

# Connect to Ableton Live and create instruments for all MIDI tracks
instruments = create_ableton_instruments()

# Access instruments by track name (converted to snake_case)
# Track "Bass" becomes instruments['bass']
# Track "Lead Synth" becomes instruments['lead_synth']
bass = instruments['bass'].out
lead = instruments['lead_synth'].out

# Use with players - sends MIDI notes and controls device parameters
# b1 >> bass([0, 2, 4], dur=1/4)

# Control device parameters using track_device_parameter naming:
# b1 >> bass([0, 2, 4], bass_operator_cutoff=0.5)

# Or with the facade automatically adding track prefix:
# b1 >> bass([0, 2, 4], operator_cutoff=0.5)

# You can use Patterns for parameter automation:
# from renardo_lib import Pattern
# l1 >> lead([7, 9, 11], dur=1/2, analog_frequency=Pattern([0.2, 0.8]))

# View the parameter map to see available parameters:
# instruments['_project'].print_parameter_map()

# Example full usage:
# b1 >> bass([0, 2, 4, 5], dur=1/4, operator_cutoff=linvar([0.2, 0.8], 8))
# l1 >> lead([7, 9, 11], dur=1/2, analog_resonance=0.6)