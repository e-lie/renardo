"""
Logging configuration for renardo.
Writes to platformdirs user log directory. No console output by default.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict


def _get_log_dir() -> Path:
    if os.environ.get("RENARDO_WEB_MODE") == "electron":
        import tempfile
        log_dir = Path(tempfile.gettempdir()) / "renardo-logs"
    else:
        from platformdirs import user_log_dir
        log_dir = Path(user_log_dir("renardo"))
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _make_logger(name: str, log_file: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    log_path = _get_log_dir() / log_file
    handler = logging.FileHandler(log_path, mode='a')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)
    return logger


# Global logger instances
_main_logger = None
_to_webclient_logger = None
_from_webclient_logger = None


def get_main_logger() -> logging.Logger:
    global _main_logger
    if _main_logger is None:
        _main_logger = _make_logger('renardo.main', 'renardo-main.log')
    return _main_logger


def get_to_webclient_logger() -> logging.Logger:
    global _to_webclient_logger
    if _to_webclient_logger is None:
        _to_webclient_logger = _make_logger('renardo.to_webclient', 'renardo-to-webclient.log')
    return _to_webclient_logger


def get_from_webclient_logger() -> logging.Logger:
    global _from_webclient_logger
    if _from_webclient_logger is None:
        _from_webclient_logger = _make_logger('renardo.from_webclient', 'renardo-from-webclient.log')
    return _from_webclient_logger


def create_subprocess_logger(
    process_type: str,
    process_id: str,
    include_timestamp: bool = True,
    log_dir: Optional[Path] = None
) -> logging.Logger:
    logger_name = f'renardo.process.{process_type}.{process_id}'
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if log_dir is None:
        log_dir = _get_log_dir()

    log_path = log_dir / f"renardo-{process_type}-{process_id}.log"
    handler = logging.FileHandler(str(log_path), mode='a')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)
    return logger


def set_log_level(level: str, logger_name: Optional[str] = None):
    level_int = getattr(logging, level.upper(), logging.INFO)
    if logger_name:
        names = [f'renardo.{logger_name}']
    else:
        names = ['renardo.main', 'renardo.to_webclient', 'renardo.from_webclient']
    for name in names:
        logger = logging.getLogger(name)
        logger.setLevel(level_int)
        for handler in logger.handlers:
            handler.setLevel(level_int)


# Backward compatibility
def get_logger(name: str) -> logging.Logger:
    if name.lower() in ['ws', 'websocket', 'web']:
        return get_to_webclient_logger()
    return get_main_logger()

def get_ws_logger() -> logging.Logger:
    return get_to_webclient_logger()

def configure_logging(config_file=None, separate_log_files: bool = True):
    pass

def add_websocket_connection(ws):
    pass

def remove_websocket_connection(ws):
    pass

def list_loggers() -> Dict[str, str]:
    return {
        name: logging.getLevelName(logging.getLogger(f'renardo.{name}').level)
        for name in ['main', 'to_webclient', 'from_webclient']
    }

def enable_debug():
    set_log_level('DEBUG')

def disable_debug():
    set_log_level('INFO')
