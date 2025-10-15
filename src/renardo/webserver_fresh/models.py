from typing import List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Author:
    id: str
    name: str
    email: str


@dataclass
class Post:
    id: str
    title: str
    content: str
    created_at: datetime
    author_id: str


# Sample data for the prototype
SAMPLE_AUTHORS = [
    Author(id="1", name="Alice Johnson", email="alice@example.com"),
    Author(id="2", name="Bob Smith", email="bob@example.com"),
    Author(id="3", name="Carol Brown", email="carol@example.com"),
]

SAMPLE_POSTS = [
    Post(
        id="1",
        title="Getting Started with Renardo",
        content="Renardo is a powerful livecoding environment that allows you to create music in real-time. In this post, we'll explore the basics of getting started with Renardo and some fundamental concepts you need to know.",
        created_at=datetime(2024, 10, 1, 10, 0, 0),
        author_id="1"
    ),
    Post(
        id="2",
        title="Advanced Patterns in Livecoding",
        content="Once you've mastered the basics, it's time to dive into more advanced patterns. This post covers complex rhythmic patterns, polyphonic sequences, and dynamic parameter modulation.",
        created_at=datetime(2024, 10, 5, 14, 30, 0),
        author_id="2"
    ),
    Post(
        id="3",
        title="Building Interactive Performances",
        content="Livecoding isn't just about writing code - it's about creating interactive, dynamic performances. Learn how to structure your code for live performance and engage with your audience.",
        created_at=datetime(2024, 10, 10, 16, 45, 0),
        author_id="1"
    ),
    Post(
        id="4",
        title="Collaborative Livecoding Techniques",
        content="Working with other musicians and coders can create amazing collaborative experiences. This post explores different techniques for collaborative livecoding sessions.",
        created_at=datetime(2024, 10, 12, 11, 15, 0),
        author_id="3"
    ),
    Post(
        id="5",
        title="Understanding SuperCollider Integration",
        content="Renardo's power comes from its integration with SuperCollider. Learn how to leverage SuperCollider's synthesis capabilities to create unique sounds.",
        created_at=datetime(2024, 10, 14, 9, 20, 0),
        author_id="2"
    ),
]