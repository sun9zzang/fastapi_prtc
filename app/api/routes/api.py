from fastapi import APIRouter

from app.api.routes import tasks, users, login, registration

router = APIRouter()
router.include_router(tasks.router, tags=["tasks"], prefix="/tasks")
router.include_router(users.router, tags=["users"], prefix="/user")
router.include_router(login.router, tags=["login"], prefix="/login")
router.include_router(registration.router, tags=["register"], prefix="/register")
