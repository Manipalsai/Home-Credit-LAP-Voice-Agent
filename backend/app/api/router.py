from fastapi import APIRouter
from backend.app.api.health import router as health_router
from backend.app.api.conversation import router as conversation_router
from backend.app.api.simulator import router as simulator_router
from backend.app.api.voice import router as voice_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(conversation_router)
api_router.include_router(simulator_router)
api_router.include_router(voice_router)
