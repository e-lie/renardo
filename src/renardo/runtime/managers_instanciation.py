
import time

from renardo.settings_manager import settings

from renardo.gatherer import SamplePackLibrary, ensure_renardo_samples_directory

from renardo.gatherer import SCResourceLibrary, ensure_sccode_directories

from renardo.sc_backend import BufferManager, ServerManager, EffectManager, SCEffect, FileEffect

# DefaultServer = SCLangServerManager(settings.get("sc_backend.ADDRESS"), PORT, settings.get("sc_backend.PORT2"))
Server = ServerManager(settings.get("sc_backend.ADDRESS"), settings.get("sc_backend.PORT"), settings.get("sc_backend.PORT2"))

_SC_POLL_INTERVAL = 5   # seconds between retries
_SC_MAX_WAIT      = 120  # total seconds before giving up

_sc_ready = Server.test_connection()
if not _sc_ready:
    print(f"SuperCollider not ready. Retrying every {_SC_POLL_INTERVAL}s (up to {_SC_MAX_WAIT}s)...")
    _deadline = time.monotonic() + _SC_MAX_WAIT
    _attempt = 0
    while not _sc_ready and time.monotonic() < _deadline:
        time.sleep(_SC_POLL_INTERVAL)
        _attempt += 1
        _sc_ready = Server.test_connection()
        if _sc_ready:
            print(f"SuperCollider connected after {_attempt} attempt(s).")
        else:
            print(f"SuperCollider not ready (attempt {_attempt}), retrying in {_SC_POLL_INTERVAL}s...")
    if not _sc_ready:
        print(f"Warning: SuperCollider did not respond after {_SC_MAX_WAIT}s, continuing anyway...")

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

## reaper_backend_fresh — pas de resource library serveur, les ressources viennent du DAW

SynthDefs = {}

effect_manager = EffectManager()
Effects = effect_manager  # Alias - to become default
SCEffect.set_server(Server)
FileEffect.set_server(Server)