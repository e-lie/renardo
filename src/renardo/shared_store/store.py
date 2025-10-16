"""
Core SharedStore class for Renardo persistent storage.
Based on diskcache with extensible architecture.
"""

from typing import Dict, Any, Optional, Type
from diskcache import Cache
from pathlib import Path
import uuid


class SharedStore:
    """
    Core persistent store for Renardo
    - Extensible architecture for different data types
    - Session-based storage with CRUD operations
    """

    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            # Default to user's home directory
            home = Path.home()
            cache_dir = home / ".renardo" / "shared_store"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache = Cache(str(self.cache_dir))
        self._current_session_id: Optional[str] = None

    def _serialize(self, obj: Any) -> Any:
        """Convert objects to serializable format"""
        from datetime import datetime
        from dataclasses import asdict

        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dataclass_fields__'):
            return {
                k: self._serialize(v)
                for k, v in asdict(obj).items()
            }
        elif isinstance(obj, list):
            return [self._serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        return obj

    def _deserialize(self, data: Any, cls: type) -> Any:
        """Rebuild objects from serialized format"""
        from datetime import datetime
        from typing import Union

        if not data:
            return None

        kwargs = {}
        for field_name, field_type in cls.__annotations__.items():
            if field_name not in data:
                continue

            value = data[field_name]

            # Handle datetime
            if field_type == datetime and isinstance(value, str):
                kwargs[field_name] = datetime.fromisoformat(value)

            # Handle Optional[datetime]
            elif hasattr(field_type, '__origin__') and field_type.__origin__ == Union:
                args = getattr(field_type, '__args__', ())
                if datetime in args and type(None) in args and isinstance(value, str):
                    kwargs[field_name] = datetime.fromisoformat(value)
                else:
                    kwargs[field_name] = value

            # Handle List of dataclasses
            elif hasattr(field_type, '__origin__') and field_type.__origin__ == list:
                inner_type = field_type.__args__[0]
                if hasattr(inner_type, '__dataclass_fields__'):
                    kwargs[field_name] = [
                        self._deserialize(item, inner_type)
                        for item in value
                    ]
                else:
                    kwargs[field_name] = value

            # Handle nested dataclass
            elif hasattr(field_type, '__dataclass_fields__'):
                kwargs[field_name] = self._deserialize(value, field_type)

            else:
                kwargs[field_name] = value

        return cls(**kwargs)

    def save(self, key: str, data: Any):
        """Save data to cache"""
        self.cache[key] = self._serialize(data)

    def load(self, key: str, cls: type = None):
        """Load data from cache"""
        data = self.cache.get(key)
        if data and cls:
            return self._deserialize(data, cls)
        return data

    def delete(self, key: str):
        """Delete data from cache"""
        if key in self.cache:
            del self.cache[key]

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        return key in self.cache

    def keys(self, pattern: str = None):
        """Get all keys, optionally filtered by pattern"""
        # diskcache.Cache is iterable but doesn't have .keys() method
        all_keys = list(self.cache)
        if pattern:
            return [k for k in all_keys if pattern in k]
        return all_keys

    def close(self):
        """Close the store"""
        self.cache.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def store_method(func):
    """
    Decorator for assigning functions as SharedStore methods.
    Similar to @player_method in Renardo's Player system.

    Usage:
    @store_method
    def add_log(self, ...):
        pass
    """
    setattr(SharedStore, func.__name__, func)
    return getattr(SharedStore, func.__name__)


# Global store instance
_global_store: Optional[SharedStore] = None


def get_shared_store() -> SharedStore:
    """Get the global shared store instance"""
    global _global_store
    if _global_store is None:
        _global_store = SharedStore()
        # Auto-register available plugins
        _register_default_plugins(_global_store)
    return _global_store


def initialize_shared_store(cache_dir: str = None, command: str = None) -> SharedStore:
    """Initialize the global shared store with specific settings"""
    global _global_store
    _global_store = SharedStore(cache_dir)
    _register_default_plugins(_global_store)

    # Start a session if command is provided
    if command:
        _global_store.start_session(command=command)

    return _global_store


def close_shared_store():
    """Close the global shared store"""
    global _global_store
    if _global_store:
        _global_store.close()
        _global_store = None


def _register_default_plugins(store: SharedStore):
    """Register default plugins"""
    # Import here to avoid circular imports
    try:
        from . import logs  # Just import to trigger @store_method registrations
    except ImportError:
        pass  # Plugin not available