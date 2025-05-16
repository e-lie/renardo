from renardo.settings_manager import settings
from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary, ensure_reaper_directories
from renardo.gatherer.reaper_resource_management.reaper_resource_file import ReaperResourceFile
from renardo.lib.music_resource import ResourceType
from pathlib import Path


#reaper_library_path = settings.get_path("REAPER_LIBRARY")
#reaper_library = ReaperResourceLibrary(reaper_library_path)


# # Example usage
# if __name__ == "__main__":
#     # Example directory structure:
#     # plugins/
#     #   0_basic_plugins/
#     #     instruments/
#     #       bass/
#     #         massive_bass.track
#     #         serum_bass.track
#     #       lead/
#     #         analog_lead.track
#     #     effects/
#     #       reverb/
#     #         pro_r.track
#     #       delay/
#     #         h_delay.track
#


# # List all banks
# print("Available plugin banks:")
# for bank_name in library.list_banks():
#     print(f"  {bank_name}")
#
# # Get a specific bank
# bank = library.get_bank(0)
# if bank:
#     print(f"\nBank: {bank.name}")
#
#     print("\nInstrument categories:")
#     for category in bank.instruments:
#         print(f"  {category}")
#         for plugin in category:
#             print(f"    {plugin}")
#
#     print("\nEffect categories:")
#     for category in bank.effects:
#         print(f"  {category}")
#         for plugin in category:
#             print(f"    {plugin}")
#
#     # Get a specific instrument
#     bass = bank.get_resource(ResourceType.INSTRUMENT, "bass", "massive_bass")
#     if bass:
#         print(f"\nFound instrument: {bass}")
#
#     # Get a specific effect
#     reverb = bank.get_resource(ResourceType.EFFECT, "reverb", "pro_r")
#     if reverb:
#         print(f"Found effect: {reverb}")