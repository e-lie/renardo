"""
Ableton Live backend service.

Manages creation of AbletonInstrument player instances inside the Renardo
runtime subprocess.  Status is tracked server-side (optimistic: set to
"running" after the init code is sent, "stopped" after cleanup code).
"""

from ...logger import get_main_logger
from ...settings_manager import settings


# Sent once at init — scans Ableton and binds each track to a global Player
_INIT_CODE = """\
from renardo.ableton_backend.ableton_instruments import create_ableton_instruments as _cai
ableton_instruments = _cai()
for _abl_k, _abl_v in ableton_instruments.items():
    if _abl_k != '_project':
        globals()[_abl_k] = _abl_v.out
print("Ableton backend initialized:", [k for k in ableton_instruments if k != '_project'])
"""

# Cleanup: removes the global Player vars and the instruments dict
_STOP_CODE = """\
if 'ableton_instruments' in globals():
    for _abl_k in [k for k in ableton_instruments if k != '_project']:
        if _abl_k in globals():
            del globals()[_abl_k]
    del globals()['ableton_instruments']
print("Ableton backend stopped")
"""


class AbletonService:
    """Thin wrapper that sends Python snippets to the runtime subprocess."""

    def __init__(self):
        self.logger = get_main_logger()
        self._status: str = "stopped"  # "stopped" | "running" | "error"

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _execute(self, code: str) -> bool:
        from ..runtime.service import runtime_service
        return runtime_service.execute_code(code)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> dict:
        if not self._execute(_INIT_CODE):
            self._status = "error"
            return {
                "success": False,
                "status": self._status,
                "message": "Runtime is not running — start it first",
            }
        self._status = "running"
        self.logger.info("Ableton init code sent to runtime")
        return {"success": True, "status": self._status, "message": "Ableton init code sent to runtime"}

    def stop(self) -> dict:
        self._execute(_STOP_CODE)
        self._status = "stopped"
        self.logger.info("Ableton backend stopped")
        return {"success": True, "status": self._status, "message": "Ableton backend stopped"}

    def restart(self) -> dict:
        self.stop()
        return self.start()

    def get_status(self) -> dict:
        return {"status": self._status, "message": f"Ableton backend {self._status}"}

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def is_startup_enabled(self) -> bool:
        return bool(settings.get("ableton_backend.ABLETON_BACKEND_ENABLED"))

    def set_startup_enabled(self, enabled: bool) -> bool:
        try:
            settings.set("ableton_backend.ABLETON_BACKEND_ENABLED", enabled)
            settings.save_to_file()
            return True
        except Exception as e:
            self.logger.error(f"Error saving Ableton startup setting: {e}")
            return False


ableton_service = AbletonService()
