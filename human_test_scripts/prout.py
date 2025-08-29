from renardo.reaper_backend.reaside import ReaperClient, Reaper
client = ReaperClient()
reaper = Reaper(client)
project = reaper.current_project
print(project.name)