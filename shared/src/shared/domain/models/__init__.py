from .user import User, UserWithSessionString
from .post import Post
from .chat import Chat
from .post_request import SendPostRequest
from .worker_message import WorkerMessage
from .story_request import PublishStoryRequest
from .analytics_service import Service
from .post_to_publish import PostToPublish
from .story_to_publish import StoryToPublish
from .story import Story
from .proxy import Proxy

from typing import TypeVar

SendingRequest = TypeVar(
    "SendingRequest",
    SendPostRequest,
    PublishStoryRequest,
)

Publication = TypeVar(
    "Publication",
    PostToPublish,
    StoryToPublish,
)


__all__ = [
    "User",
    "Post",
    "Chat",
    "SendPostRequest",
    "PublishStoryRequest",
    "WorkerMessage",
    "UserWithSessionString",
    "SendingRequest",
    "Service",
    "PostToPublish",
    "StoryToPublish",
    "Story",
    "Proxy"
]

Proxy.model_rebuild()
