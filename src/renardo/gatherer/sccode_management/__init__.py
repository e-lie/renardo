from renardo.settings_manager import settings
from renardo.gatherer.sccode_management.scresource_library import SCResourceLibrary, ensure_sccode_directories
from renardo.gatherer.sccode_management.scresource_type_and_file import SCResourceFile
from renardo.lib.music_resource import ResourceType
from pathlib import Path


#sccode_library_path = settings.get_path("SCCODE_LIBRARY")
#sccode_library = SCResourceLibrary(sccode_library_path)


# # Example usage
# if __name__ == "__main__":
#     # Example directory structure:
#     # synthdefs/
#     #   0_basic_synths/
#     #     instruments/
#     #       bass/
#     #         sub_bass.scsyndef
#     #         wobble_bass.scsyndef
#     #       lead/
#     #         saw_lead.scsyndef
#     #     effects/
#     #       reverb/
#     #         plate_reverb.scsyndef
#     #       delay/
#     #         tape_delay.scsyndef
#


# # List all banks
# print("Available synthdef banks:")
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
#         for synthdef in category:
#             print(f"    {synthdef}")
#
#     print("\nEffect categories:")
#     for category in bank.effects:
#         print(f"  {category}")
#         for synthdef in category:
#             print(f"    {synthdef}")
#
#     # Get a specific instrument
#     bass = bank.get_synthdef(SCResourceType.INSTRUMENT, "bass", "sub_bass")
#     if bass:
#         print(f"\nFound instrument: {bass}")
#
#     # Get a specific effect
#     reverb = bank.get_synthdef(SCResourceType.EFFECT, "reverb", "plate_reverb")
#     if reverb:
#         print(f"Found effect: {reverb}")