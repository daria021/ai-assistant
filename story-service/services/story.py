# File: story-service/app/services/story.py
import logging
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient
from telethon.sessions import StringSession

from abstractions.repositories import UserRepositoryInterface
from abstractions.repositories.story import StoryRepositoryInterface
from abstractions.services.story import StoryServiceInterface
from domain.dto.story import CreateStoryDTO
from infrastructure.enums.story_status import StoryStatus
from infrastructure.repositories.story import StoryRepository
from user_bot.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class StoryService(StoryServiceInterface):
    story_repository: StoryRepositoryInterface
    user_repository: UserRepositoryInterface


    async def create_story(self, story: CreateStoryDTO):
        await self.story_repository.create(story)


    async def publish_story(self, story_id: UUID):
        story = await self.story_repository.get(story_id)
        if not story or story.status != StoryStatus.pending:
            return
        manager = await self.user_repository.get(story.manager_id)

        client = TelegramClient(
            StringSession(manager.session_string),
            api_id=settings.telegram_api_id,
            api_hash=settings.telegram_api_hash,
        )
        await client.start()
        try:
            await client.send_file("me", story.file_path, story=True)
            story.status = StoryStatus.posted
            await session.commit()
            logger.info(f"Posted story {story_id} for manager {manager.id}")
        except Exception as e:
            logger.error(f"Failed to post story {story_id}: {e}")
        finally:
            await client.disconnect()
