# File: story-service/app/routes/admin.py
from fastapi import APIRouter, HTTPException

from dependencies.services.user import get_user_service
from domain.dto.user import CreateUserDTO

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post("/")
async def create_manager(user: CreateUserDTO):
    user_service = get_user_service()
    return user_service.create_user(user)
