
#from .reaper_backend_init import reainstru_factory


# Reaper integration
# add_multiple_fxchains = reainstru_factory.add_multiple_fxchains
# create_instrument_facade = reainstru_factory.create_instrument_facade

# def instanciate(track_name, chain_name, scan_all_params=True, is_chain=True):
#     try:
#         facade_obj = create_instrument_facade(name=chain_name, plugin_name=chain_name, track_name=track_name, scan_all_params=scan_all_params, is_chain=is_chain)
#         return facade_obj
#     except Exception as e:
#         print(f"Error adding chain {chain_name}: {e}")
#         return None