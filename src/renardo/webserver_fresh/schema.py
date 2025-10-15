import strawberry
from typing import List, Optional
from datetime import datetime
from .models import SAMPLE_AUTHORS, SAMPLE_POSTS, Author as AuthorModel, Post as PostModel


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


schema = strawberry.Schema(query=Query)