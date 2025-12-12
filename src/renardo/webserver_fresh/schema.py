import strawberry
from typing import List, Optional, AsyncGenerator
from datetime import datetime
import asyncio
from collections import deque
from .models import SAMPLE_AUTHORS, SAMPLE_POSTS, Author as AuthorModel, Post as PostModel
from ..shared_store import get_shared_store


@strawberry.type
class Author:
    id: str
    name: str
    email: str

    @strawberry.field
    def posts(self) -> List["Post"]:
        return [
            Post(
                id=post.id,
                title=post.title,
                content=post.content,
                created_at=post.created_at,
                author_id=post.author_id
            )
            for post in SAMPLE_POSTS
            if post.author_id == self.id
        ]


@strawberry.type
class Post:
    id: str
    title: str
    content: str
    created_at: datetime
    author_id: str

    @strawberry.field
    def author(self) -> Author:
        author_model = next(
            (author for author in SAMPLE_AUTHORS if author.id == self.author_id),
            None
        )
        if not author_model:
            raise ValueError(f"Author not found for ID: {self.author_id}")

        return Author(
            id=author_model.id,
            name=author_model.name,
            email=author_model.email
        )


@strawberry.type
class LogEntry:
    id: str
    timestamp: datetime
    level: str
    logger: str
    source: str
    message: str
    extra: Optional[str] = None


@strawberry.type
class ExecuteCodeResult:
    success: bool
    message: str
    output: Optional[str] = None


@strawberry.type
class Mutation:
    @strawberry.field
    def execute_code(self, code: str) -> ExecuteCodeResult:
        """Execute Python code in the Renardo runtime"""
        try:
            # Import the execute function from renardo runtime
            from ..runtime import execute
            
            # Execute the code
            result = execute(code, verbose=True)
            
            return ExecuteCodeResult(
                success=True,
                message="Code executed successfully",
                output=str(result) if result else None
            )
        except Exception as e:
            return ExecuteCodeResult(
                success=False,
                message=f"Error executing code: {str(e)}",
                output=None
            )


@strawberry.type
class Query:
    @strawberry.field
    def posts(self) -> List[Post]:
        return [
            Post(
                id=post.id,
                title=post.title,
                content=post.content,
                created_at=post.created_at,
                author_id=post.author_id
            )
            for post in SAMPLE_POSTS
        ]

    @strawberry.field
    def authors(self) -> List[Author]:
        return [
            Author(
                id=author.id,
                name=author.name,
                email=author.email
            )
            for author in SAMPLE_AUTHORS
        ]

    @strawberry.field
    def post(self, id: str) -> Optional[Post]:
        post_model = next(
            (post for post in SAMPLE_POSTS if post.id == id),
            None
        )
        if not post_model:
            return None

        return Post(
            id=post_model.id,
            title=post_model.title,
            content=post_model.content,
            created_at=post_model.created_at,
            author_id=post_model.author_id
        )

    @strawberry.field
    def author(self, id: str) -> Optional[Author]:
        author_model = next(
            (author for author in SAMPLE_AUTHORS if author.id == id),
            None
        )
        if not author_model:
            return None

        return Author(
            id=author_model.id,
            name=author_model.name,
            email=author_model.email
        )

    @strawberry.field
    def historical_logs(self, limit: int = 1000) -> List[LogEntry]:
        """Get historical logs from persistent storage"""
        try:
            store = get_shared_store()
            stored_logs = store.get_recent_logs(limit)

            # Convert shared_store.LogEntry to GraphQL LogEntry
            return [
                LogEntry(
                    id=log.id,
                    timestamp=log.timestamp,
                    level=log.level,
                    logger=log.logger,
                    source=log.source,
                    message=log.message,
                    extra=log.extra
                )
                for log in stored_logs
            ]
        except Exception as e:
            print(f"Error fetching historical logs: {e}")
            return []


# Global log buffer for subscriptions
LOG_BUFFER: deque = deque(maxlen=1000)
LOG_SUBSCRIBERS: List[asyncio.Queue] = []


async def broadcast_log(log_entry: LogEntry):
    """Broadcast a log entry to all subscribers"""
    LOG_BUFFER.append(log_entry)
    for queue in LOG_SUBSCRIBERS:
        try:
            await queue.put(log_entry)
        except:
            pass  # Ignore closed queues


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def logs(self, filter_level: Optional[str] = None) -> AsyncGenerator[LogEntry, None]:
        """Subscribe to real-time log updates"""
        queue = asyncio.Queue()
        LOG_SUBSCRIBERS.append(queue)

        try:
            # Send existing logs from buffer
            for log in LOG_BUFFER:
                if not filter_level or log.level == filter_level:
                    yield log

            # Stream new logs as they arrive
            while True:
                log_entry = await queue.get()
                if not filter_level or log_entry.level == filter_level:
                    yield log_entry
        finally:
            # Clean up when subscription ends
            if queue in LOG_SUBSCRIBERS:
                LOG_SUBSCRIBERS.remove(queue)


schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)