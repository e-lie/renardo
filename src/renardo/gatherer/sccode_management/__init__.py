from renardo import settings
from renardo.gatherer.sccode_management.sccode_library import SCCodeLibrary
from renardo.gatherer.sccode_management.sccode_type_and_file import SCCodeType
from pathlib import Path

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

sccode_library = SCCodeLibrary(settings.get("sc_backend.SCCODE_LIBRARY"))

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
#     bass = bank.get_synthdef(SCCodeType.INSTRUMENT, "bass", "sub_bass")
#     if bass:
#         print(f"\nFound instrument: {bass}")
#
#     # Get a specific effect
#     reverb = bank.get_synthdef(SCCodeType.EFFECT, "reverb", "plate_reverb")
#     if reverb:
#         print(f"Found effect: {reverb}")