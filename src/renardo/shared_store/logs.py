"""
Logs plugin for SharedStore with LogEntry, LogSession and CRUD operations.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
import json
from .store import store_method


@dataclass
class LogEntry:
    """Individual log entry"""
    id: str
    timestamp: datetime
    level: str  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    logger: str  # Logger name (e.g., 'renardo.main')
    source: str  # Source type (e.g., 'renardo', 'subprocess')
    process: str  # Process name (e.g., 'BACKEND', 'FRONTEND', 'FLOK')
    module_path: Optional[str] = None  # Path to the module that logged
    message: str = ""
    extra: Optional[Dict[str, Any]] = None


@dataclass
class LogSession:
    """Log session representing one Renardo startup"""
    id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    command: Optional[str] = None  # Command used to start (e.g., 'uv run cli --webclient')
    pid: Optional[int] = None  # Process ID
    logs: List[LogEntry] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@store_method
def start_session(self, command: str = None, pid: int = None) -> LogSession:
    """Start a new logging session"""
    # End current session if exists
    current_session = self.get_current_session()
    if current_session:
        self.end_current_session()

    session_id = str(uuid.uuid4())
    session = LogSession(
        id=session_id,
        start_time=datetime.now(),
        command=command,
        pid=pid or os.getpid()
    )

    # Save initial session
    self._save_session(session)

    # Set as current session
    self._current_session_id = session_id
    self.save('current_session', session_id)

    # Prune old sessions
    self._prune_old_sessions()

    return session


@store_method
def end_current_session(self):
    """End the current logging session"""
    if self._current_session_id:
        session = self.get_session(self._current_session_id)
        if session:
            session.end_time = datetime.now()
            self._save_session(session)

        self._current_session_id = None
        self.delete('current_session')


@store_method
def get_current_session(self) -> Optional[LogSession]:
    """Get the current active session"""
    if self._current_session_id:
        return self.get_session(self._current_session_id)

    # Try to load from cache
    current_id = self.load('current_session')
    if current_id:
        self._current_session_id = current_id
        return self.get_session(current_id)

    return None


@store_method
def _save_session(self, session: LogSession):
    """Save session to cache"""
    key = f"session:{session.id}"
    self.save(key, session)


@store_method
def get_session(self, session_id: str) -> Optional[LogSession]:
    """Get a specific session"""
    key = f"session:{session_id}"
    return self.load(key, LogSession)


@store_method
def add_log(self,
            level: str,
            logger: str,
            message: str,
            source: str = "renardo",
            process: str = "MAIN",
            module_path: str = None,
            extra: Dict[str, Any] = None) -> LogEntry:
    """Add a log entry to the current session"""

    # Ensure we have a current session
    current_session = self.get_current_session()
    if not current_session:
        current_session = self.start_session()

    log_entry = LogEntry(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        level=level,
        logger=logger,
        source=source,
        process=process,
        module_path=module_path,
        message=message,
        extra=extra
    )

    # Add to current session
    current_session.logs.append(log_entry)

    # Save session (efficient with diskcache)
    self._save_session(current_session)

    return log_entry


@store_method
def get_all_sessions(self) -> List[LogSession]:
    """Get all sessions ordered by start time (newest first)"""
    sessions = []
    session_keys = self._get_session_keys()

    for key in session_keys:
        session = self.get_session(key.replace('session:', ''))
        if session:
            sessions.append(session)

    return sessions


@store_method
def get_recent_logs(self, limit: int = 1000) -> List[LogEntry]:
    """Get recent logs across all sessions"""
    all_logs = []

    for session in self.get_all_sessions():
        all_logs.extend(session.logs)

    # Sort by timestamp (newest first)
    all_logs.sort(key=lambda log: log.timestamp, reverse=True)

    return all_logs[:limit]


@store_method
def search_logs(self,
               query: str = None,
               level: str = None,
               logger: str = None,
               source: str = None,
               process: str = None,
               start_time: datetime = None,
               end_time: datetime = None,
               limit: int = 1000) -> List[LogEntry]:
    """Search logs with filters"""

    all_logs = self.get_recent_logs(limit * 2)  # Get more to filter
    filtered_logs = []

    for log in all_logs:
        # Apply filters
        if level and log.level != level:
            continue
        if logger and logger not in log.logger:
            continue
        if source and log.source != source:
            continue
        if process and log.process != process:
            continue
        if start_time and log.timestamp < start_time:
            continue
        if end_time and log.timestamp > end_time:
            continue
        if query and query.lower() not in log.message.lower():
            continue

        filtered_logs.append(log)

        if len(filtered_logs) >= limit:
            break

    return filtered_logs


@store_method
def get_session_stats(self) -> Dict[str, Any]:
    """Get statistics about stored sessions"""
    sessions = self.get_all_sessions()

    if not sessions:
        return {
            'total_sessions': 0,
            'total_logs': 0,
            'active_session': None
        }

    total_logs = sum(len(session.logs) for session in sessions)
    current_session = self.get_current_session()

    return {
        'total_sessions': len(sessions),
        'total_logs': total_logs,
        'active_session': current_session.id if current_session else None,
        'oldest_session': sessions[-1].start_time if sessions else None,
        'newest_session': sessions[0].start_time if sessions else None,
        'cache_size': len(self.cache),
        'cache_dir': str(self.cache_dir)
    }


@store_method
def export_session(self, session_id: str, format: str = 'json') -> str:
    """Export a session to JSON or other format"""
    session = self.get_session(session_id)
    if not session:
        return ""

    if format == 'json':
        return json.dumps(self._serialize(session), indent=2, default=str)

    # TODO: Add other formats (txt, csv, etc.)
    return ""


@store_method
def _get_session_keys(self) -> List[str]:
    """Get all session keys sorted by start time"""
    session_keys = []
    for key in self.keys():
        if isinstance(key, str) and key.startswith('session:'):
            session_keys.append(key)

    # Sort by session start time
    session_keys.sort(key=lambda k: self._get_session_start_time(k), reverse=True)
    return session_keys


@store_method
def _get_session_start_time(self, session_key: str) -> datetime:
    """Get start time of a session for sorting"""
    try:
        session_data = self.cache.get(session_key)
        if session_data and 'start_time' in session_data:
            return datetime.fromisoformat(session_data['start_time'])
    except:
        pass
    return datetime.min


@store_method
def _prune_old_sessions(self):
    """Keep only the last 5 sessions"""
    session_keys = self._get_session_keys()

    if len(session_keys) > 5:
        # Remove oldest sessions
        for old_key in session_keys[5:]:
            try:
                self.delete(old_key)
            except:
                pass