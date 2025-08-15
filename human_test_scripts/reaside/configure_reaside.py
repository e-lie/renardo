
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside import configure_reaper



configure_reaper()


# print("=== Simple Track Scan Test ===")

# # Initialize client
# client = ReaperClient()

# reaper = Reaper(client)
# project = reaper.current_project

# # Create track
# track = project.add_track()
# track.name = "Scan Test Track"

# fx_list = ["ReaEQ", "ReaComp", "ReaVerb"]
# for fx_name in fx_list:
#     fx_index = track.add_fx(fx_name)
#     print(f"   Added {fx_name} -> result: {fx_index}")
