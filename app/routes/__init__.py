from fastapi import APIRouter
from app.routes import user

router = APIRouter()
router.include_router(user.router)
