"""
Log handler to capture Renardo logs and broadcast them via GraphQL subscriptions.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
import uuid

from .schema import LogEntry, broadcast_log


class GraphQLLogHandler(logging.Handler):
    """Custom log handler that broadcasts logs to GraphQL subscriptions"""

    def __init__(self, source: str = "renardo"):
        super().__init__()
        self.source = source
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def emit(self, record: logging.LogRecord):
        """Emit a log record to GraphQL subscribers"""
        try:
            # Create log entry
            log_entry = LogEntry(
                id=str(uuid.uuid4()),
                timestamp=datetime.fromtimestamp(record.created),
                level=record.levelname,
                logger=record.name,
                source=self.source,
                message=self.format(record),
                extra=None
            )

            # Get or create event loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, try to get one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Schedule the broadcast
            asyncio.create_task(broadcast_log(log_entry))

        except Exception as e:
            # Silently fail to avoid infinite recursion
            pass


def setup_log_capture():
    """Setup log capture for all Renardo loggers"""
    # Create GraphQL log handler
    graphql_handler = GraphQLLogHandler(source="renardo")
    graphql_handler.setFormatter(logging.Formatter('%(message)s'))

    # Add to root logger to capture all logs
    root_logger = logging.getLogger()
    root_logger.addHandler(graphql_handler)

    # Also add to specific loggers if needed
    loggers_to_capture = [
        'renardo',
        'renardo.main',
        'renardo.process_manager',
        'renardo.logger',
        'renardo.webserver',
        'renardo.reaper'
    ]

    for logger_name in loggers_to_capture:
        logger = logging.getLogger(logger_name)
        logger.addHandler(graphql_handler)

    return graphql_handler


def capture_subprocess_output(process_name: str, line: str, level: str = "INFO"):
    """Capture output from subprocess and send to GraphQL"""
    try:
        log_entry = LogEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            level=level,
            logger=process_name,
            source="subprocess",
            message=line.strip(),
            extra=None
        )

        # Get event loop and broadcast
        loop = asyncio.get_running_loop()
        asyncio.create_task(broadcast_log(log_entry))
    except:
        pass  # Silently fail