from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside import configure_reaper
import json

# configure_reaper()

client = ReaperClient()

# Send the OSC message via ExtState
osc_message = {
  "address": "/custom/test_function",
  "args": ["arg1", "arg2"]  # Optional marker name
}

client.set_ext_state("reaside_osc", "incoming", json.dumps(osc_message))