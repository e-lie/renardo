# reaper_backend_init.py — ancien backend (ReaperInstrumentFactory, resource library)
# Remplacé par reaper_backend_fresh. Conservé pour référence.

# from renardo.runtime.managers_instanciation import reaper_resource_library
# from renardo.reaper_backend import ReaperInstrument
# from renardo.settings_manager import settings
# from pprint import pprint
# from typing import List, TypeGuard
#
# def list_selected_reaper_instruments():
#     print(settings.get("reaper_backend.SELECTED_REAPER_INSTRUMENTS"))
#
# def list_all_reaper_instruments():
#     for reaper_resource_bank in reaper_resource_library:
#         if reaper_resource_bank.name in settings.get("reaper_backend.ACTIVATED_REAPER_BANKS"):
#             print(f"Reaper instrument bank:{reaper_resource_bank.name}")
#             for instrument_category in reaper_resource_bank.instruments:
#                 print(f"Instrument category:{instrument_category.category}")
#                 instrument_list = []
#                 for reaper_resource_file in instrument_category:
#                     instrument_list.append(reaper_resource_file.name)
#                 pprint(instrument_list)
#
# def set_selected_instruments(selected_instrument_list: List[str]):
#     def is_string_list(val: List) -> TypeGuard[List[str]]:
#       return isinstance(val, list) and all(isinstance(x, str) for x in val)
#     if selected_instrument_list:
#         settings.set(("reaper_backend.SELECTED_REAPER_INSTRUMENTS"), selected_instrument_list)
#     else:
#         print("wrong argument type, expected list of string")
#
# class ReaperInstrumentFactory():
#     def __init__(self, foxdotcode_instance):
#         self._foxdotcode_instance = foxdotcode_instance
#     def __call__(self):
#         ...  # (ancien code de chargement des instruments depuis la resource library)
