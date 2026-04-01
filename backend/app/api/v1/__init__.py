from fastapi import APIRouter
from .routes.chat import router as chat_router
from .routes.delete_memory import router as delete_memory_router

router = APIRouter(prefix="/api/v1")

router.include_router(chat_router)
router.include_router(delete_memory_router)

__all__ = ["router"]
