from fastapi import APIRouter

from .user import router as user_router
from .post import router as post_router
from .story import router as story_router
from .story_to_publish import router as story_to_publish_router
from .post_to_publish import router as post_to_publish_router
from .auth import router as auth_router
from .chat import router as chat_router
from .emoji import router as emoji_router
from .upload import router as upload_router
from .chat import router as chat_router
from .chat_type import router as chat_type_router

router = APIRouter(
    prefix="/api",
)

router.include_router(user_router)
router.include_router(post_router)
router.include_router(story_router)
router.include_router(story_to_publish_router)
router.include_router(post_to_publish_router)
router.include_router(auth_router)
router.include_router(chat_router)
router.include_router(emoji_router)
router.include_router(upload_router)
router.include_router(chat_router)
router.include_router(chat_type_router)
