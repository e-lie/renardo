# from renardo.reaper_backend.reaper_music_resource import ReaperInstrument

#reainstru_factory = ReaperInstrumentFactory(old_style_presets, reaproject)
#reaper_instruments = reainstru_factory.create_all_facades_from_reaproject_tracks()

from renardo.runtime.managers_instanciation import reaper_resource_library
from renardo.reaper_backend import ReaperInstrument
from renardo.settings_manager import settings



class instanciate_reaper_instruments:

    _foxdotcode_instance = None

    @classmethod
    def set_foxdotcode_instance(cls, foxdotcode_instance):
        cls._foxdotcode_instance = foxdotcode_instance

    def __init__(self):
        num_channels_used = 0
        selected_instruments = settings.get("reaper_backend.SELECTED_REAPER_INSTRUMENTS")
        
        # If specific instruments are selected, look for them across all active banks
        if selected_instruments and len(selected_instruments) > 0:
            print(f"Looking for selected instruments: {selected_instruments}")
            instrument_count = 0
            found_instruments = set()
            
            # First pass: search for the selected instruments by shortname
            for reaper_resource_bank in reaper_resource_library:
                if reaper_resource_bank.name in settings.get("reaper_backend.ACTIVATED_REAPER_BANKS"):
                    for instrument_category in reaper_resource_bank.instruments:
                        for reaper_resource_file in instrument_category:
                            # Check if this resource's shortname is in the selected list
                            resource_name = reaper_resource_file.name
                            
                            if resource_name in selected_instruments and resource_name not in found_instruments:
                                if not num_channels_used >= 16:
                                    num_channels_used += 1
                                    # Load the resource
                                    reaper_instrument:ReaperInstrument = reaper_resource_file.load_resource_from_python()
                                    reaper_instrument.bank = reaper_resource_bank.name
                                    reaper_instrument.category = instrument_category.category
                                    
                                    if reaper_instrument:
                                        # Define the global variable for this instrument
                                        #globals()[reaper_instrument.shortname] = reaper_instrument
                                        self.__class__._foxdotcode_instance.namespace[reaper_instrument.shortname] = reaper_instrument
                                        found_instruments.add(resource_name)
                                        instrument_count += 1
                                        print(f"Loaded selected instrument: {resource_name} from {reaper_resource_bank.name}/{instrument_category.category}")
                                    else:
                                        print(f"Could not load selected instrument {resource_name} from {reaper_resource_file.path}")
                                else:
                                    print(f"Maximum channels (16) reached. Skipping remaining instruments.")
                                    break
            
            # Report on results
            if instrument_count > 0:
                print(f"Successfully loaded {instrument_count} selected instruments: {', '.join(found_instruments)}")
                # Check for instruments that were not found
                not_found = set(selected_instruments) - found_instruments
                if not_found:
                    print(f"Warning: Could not find these selected instruments: {', '.join(not_found)}")
            else:
                print("No selected instruments were found or loaded. Falling back to default behavior.")
                # Fall back to default behavior if no selected instruments were found
                self._instanciate_all_reaper_instruments()
        else:
            # No specific instruments selected, use the original behavior
            self._instanciate_all_reaper_instruments()

    def _instanciate_all_reaper_instruments(self):
        """Original implementation that loads all instruments from activated banks."""
        num_channels_used = 0
        
        for reaper_resource_bank in reaper_resource_library:
            if reaper_resource_bank.name in settings.get("reaper_backend.ACTIVATED_REAPER_BANKS"):
                for instrument_category in reaper_resource_bank.instruments:
                    for reaper_resource_file in instrument_category:
                        if not num_channels_used >= 16:
                            num_channels_used += 1
                            # load the SCInstrument instance declared in every python resource file found in library
                            reaper_instrument:ReaperInstrument = reaper_resource_file.load_resource_from_python()
                            reaper_instrument.bank = reaper_resource_bank.name
                            reaper_instrument.category = instrument_category.category
                            if reaper_instrument:
                                # define a variable for each scinstrument (callable in the context of a player and returns a InstrumentProxy)
                                globals()[reaper_instrument.shortname] = reaper_instrument
                                print(f"Loaded instrument: {reaper_instrument.shortname} from {reaper_resource_bank.name}/{instrument_category.category}")
                            else:
                                print(f"Resource from {reaper_resource_file.path} could not be loaded!")
                        else:
                            print(f"Maximum channels (16) reached. Skipping remaining instruments.")
                            break