# File: story-service/app/routes/story.py
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from datetime import datetime
import os

from dependencies.services.user import get_user_service
from domain.dto.story import CreateStoryDTO
from infrastructure.entities import Story
from ..scheduler import schedule_story
from ..settings import settings

router = APIRouter()

@router.post("/")
async def create_story(
    manager_id: UUID = Form(...),
    scheduled_time: datetime = Form(...),
    file: UploadFile = File(...),
):
    # Проверка менеджера
    user_service = get_user_service()
    mgr = user_service.get_manager(manager_id)
    if not mgr:
        raise HTTPException(status_code=404, detail="Manager not found")

    # Сохраняем файл
    os.makedirs(settings.media_dir, exist_ok=True)
    file_path = os.path.join(
        settings.media_dir,
        f"{int(datetime.utcnow().timestamp())}_{file.filename}"
    )
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Создаём запись
    story = CreateStoryDTO(manager_id=manager_id, file_path=file_path, scheduled_time=scheduled_time)
    story_service = get_story_service()

    # Планируем публикацию
    schedule_story(story.id, run_date=scheduled_time)
    return story
