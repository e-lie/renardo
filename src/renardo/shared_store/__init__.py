"""
Renardo SharedStore - Extensible persistent storage system

A modular storage system with plugin architecture for different data types.
Currently supports logging with session management and automatic pruning.
"""

from .store import (
    SharedStore,
    store_method,
    get_shared_store,
    initialize_shared_store,
    close_shared_store
)

from .logs import (
    LogEntry,
    LogSession
)

# For backward compatibility with existing code
def get_log_store():
    """Backward compatibility alias"""
    return get_shared_store()

def initialize_log_store(cache_dir: str = None, command: str = None):
    """Backward compatibility alias"""
    store = initialize_shared_store(cache_dir)
    if command:
        store.start_session(command=command)
    return store

def close_log_store():
    """Backward compatibility alias"""
    close_shared_store()

__all__ = [
    'SharedStore',
    'store_method',
    'get_shared_store',
    'initialize_shared_store',
    'close_shared_store',
    'LogEntry',
    'LogSession',
    # Backward compatibility
    'get_log_store',
    'initialize_log_store',
    'close_log_store'
]