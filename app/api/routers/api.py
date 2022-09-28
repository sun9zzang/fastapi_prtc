from fastapi import APIRouter

from app.api.routers import tasks, users

router = APIRouter()
router.include_router(tasks.router, tags=["tasks"], prefix="/tasks")
router.include_router(users.router, tags=["users"], prefix="/user")
