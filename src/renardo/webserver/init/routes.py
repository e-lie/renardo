import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter
from pydantic import BaseModel

from ..websocket.manager import websocket_manager
from ...settings_manager import SettingsManager

router = APIRouter(prefix="/api/init", tags=["init"])
_executor = ThreadPoolExecutor(max_workers=2)


def _is_user_dir_configured() -> bool:
    """Check if user directory was explicitly configured (env var or user_dir.toml)."""
    if os.environ.get("RENARDO_USER_DIR"):
        return True
    standard_dir = SettingsManager.get_standard_user_dir()
    user_dir_file = standard_dir / "user_dir.toml"
    if user_dir_file.exists():
        try:
            import tomli
            with open(user_dir_file, "rb") as f:
                config = tomli.load(f)
            return "RENARDO_USER_DIR_PATH" in config
        except Exception:
            return False
    return False


@router.get("/status")
async def get_init_status():
    """Get initialization status: user dir configured + resources downloaded."""
    from ...gatherer.sample_management.default_samples import (
        is_default_spack_initialized,
        backfill_sample_markers,
    )
    from ...gatherer.sccode_management.default_sccode_pack import (
        is_default_sccode_pack_initialized,
        is_special_sccode_initialized,
        backfill_sccode_markers,
    )

    user_dir_configured = _is_user_dir_configured()
    user_dir = str(SettingsManager.get_renardo_user_dir())

    # Backfill markers for directories that already have content (previous installs, manual setup)
    backfill_sample_markers()
    backfill_sccode_markers()

    samples_initialized = is_default_spack_initialized()
    sccode_initialized = is_default_sccode_pack_initialized() and is_special_sccode_initialized()

    return {
        "user_dir_configured": user_dir_configured,
        "user_dir": user_dir,
        "samples_initialized": samples_initialized,
        "sccode_initialized": sccode_initialized,
    }


class DownloadMissingRequest(BaseModel):
    download_samples: bool = True
    download_sccode: bool = True


@router.post("/download-missing")
async def download_missing(request: DownloadMissingRequest):
    """Start background download of missing resources, progress via WebSocket source='init'."""
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        _executor,
        lambda: _download_task(request.download_samples, request.download_sccode, loop),
    )
    return {"success": True, "message": "Download started"}


def _download_task(download_samples: bool, download_sccode: bool, loop):
    """Background task that downloads resources and streams progress via WebSocket."""

    class WsLogger:
        def _send(self, level: str, msg: str, metadata=None):
            asyncio.run_coroutine_threadsafe(
                websocket_manager.send_console_message(level, "init", msg, metadata),
                loop,
            )

        def info(self, msg):
            self._send("info", msg)

        def error(self, msg):
            self._send("error", msg)

        # default_samples.py / collection_download.py interface
        def write_line(self, msg, level=None):
            if level and level.upper() in ("WARN", "WARNING", "ERROR"):
                self._send("warn", msg)
            else:
                self._send("info", msg)

        def write_error(self, msg):
            self.error(msg)

    logger = WsLogger()
    success = True

    try:
        if download_samples:
            from ...gatherer.sample_management.default_samples import (
                is_default_spack_initialized,
                download_default_sample_pack,
            )

            if not is_default_spack_initialized():
                logger.info("Starting sample pack download...")
                result = download_default_sample_pack(logger)
                if not result:
                    logger.error("Sample pack download failed.")
                    success = False
                else:
                    logger.info("Sample pack downloaded successfully.")
            else:
                logger.info("Sample pack already initialized.")

        if download_sccode:
            from ...gatherer.sccode_management.default_sccode_pack import (
                is_default_sccode_pack_initialized,
                is_special_sccode_initialized,
                download_sccode_pack,
                provision_special_sccode_pack,
            )
            from ...settings_manager import settings as _settings

            if not is_special_sccode_initialized():
                logger.info("Provisioning special SCCode...")
                result = provision_special_sccode_pack(logger)
                if not result:
                    logger.error("Special SCCode provisioning failed.")
                    success = False
                else:
                    logger.info("Special SCCode provisioned successfully.")
            else:
                logger.info("Special SCCode already initialized.")

            if not is_default_sccode_pack_initialized():
                pack_name = _settings.get("sc_backend.DEFAULT_SCCODE_PACK_NAME")
                logger.info(f"Starting SCCode pack '{pack_name}' download...")
                result = download_sccode_pack(pack_name, logger)
                if not result:
                    logger.error(f"SCCode pack '{pack_name}' download failed.")
                    success = False
                else:
                    logger.info(f"SCCode pack '{pack_name}' downloaded successfully.")
            else:
                logger.info("SCCode pack already initialized.")

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        success = False

    if success:
        logger._send("info", "All downloads complete.", metadata={"event": "init_complete"})
    else:
        logger._send("error", "Some downloads failed.", metadata={"event": "init_error"})
