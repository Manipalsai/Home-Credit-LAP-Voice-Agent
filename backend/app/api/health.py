from fastapi import APIRouter
from backend.app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    """Health check endpoint returning system status and safe environment configuration."""
    return {
        "status": "healthy",
        "service": "Home Credit LAP Voice Agent Qualification Engine",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "configured_provider": settings.VOICE_PLATFORM,
        "features": {
            "retell_configured": bool(settings.RETELL_API_KEY and settings.RETELL_API_KEY != "your_retell_api_key_here"),
            "bolna_configured": bool(settings.BOLNA_API_KEY and settings.BOLNA_API_KEY != "your_bolna_api_key_here"),
            "llm_configured": bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here"),
        },
    }
