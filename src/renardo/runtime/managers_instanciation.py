
from renardo.settings_manager import settings

from renardo.gatherer import SamplePackLibrary, ensure_renardo_samples_directory

from renardo.gatherer import SCResourceLibrary, ensure_sccode_directories, ReaperResourceLibrary, ensure_reaper_directories

from renardo.sc_backend import BufferManager, ServerManager, EffectManager, SCEffect, FileEffect

# DefaultServer = SCLangServerManager(settings.get("sc_backend.ADDRESS"), PORT, settings.get("sc_backend.PORT2"))
Server = ServerManager(settings.get("sc_backend.ADDRESS"), settings.get("sc_backend.PORT"), settings.get("sc_backend.PORT2"))
Server.init_connection()

if settings.get("sc_backend.FORWARD_PORT") and settings.get("sc_backend.FORWARD_ADDRESS"):
    Server.add_forward(settings.get("sc_backend.FORWARD_ADDRESS"), settings.get("sc_backend.FORWARD_PORT"))

ensure_renardo_samples_directory()
sample_pack_library = SamplePackLibrary(settings.get_path("SAMPLES_DIR"), [])
sample_packs = sample_pack_library

# Samples and DefaultSamples just display default samples list (compat with FoxDot print(Samples))
DefaultSamples = Samples = "\n".join(["%r: %s" % (k, v) for k, v in sorted(settings.get("samples.SYMBOLS_DESCRIPTION").items())])
buffer_manager =  BufferManager(server=Server, sample_library=sample_pack_library)


ensure_sccode_directories()
scresource_library = SCResourceLibrary(settings.get_path("SCCODE_LIBRARY"))

## Conditionnal init of reaper backend resource library
if settings.get("reaper_backend.REAPER_BACKEND_ENABLED"):
    ensure_reaper_directories()
    reaper_resource_library = ReaperResourceLibrary(settings.get_path("REAPER_LIBRARY"))

SynthDefs = {}

effect_manager = EffectManager()
Effects = effect_manager  # Alias - to become default
SCEffect.set_server(Server)
FileEffect.set_server(Server)