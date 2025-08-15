from renardo.reaper_backend.reaside import ReaperClient, Reaper


# Initialize client
client = ReaperClient()

reaper = Reaper(client)
project = reaper.current_project

# Create track
track = project.add_track()
track.name = "Vital Test Track"

vital_fx = track.add_fx("VST3i: Vital (Vital Audio)")
