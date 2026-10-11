from fastapi import APIRouter, Request, Header, HTTPException, status
from typing import Optional, Dict, Any
import json

from backend.app.voice.retell_adapter import retell_adapter
from backend.app.voice.bolna_adapter import bolna_adapter
from backend.app.voice.webhook_verifier import WebhookVerifier
from backend.app.models.voice_payloads import WebhookResponse
from backend.app.config import settings

router = APIRouter(prefix="/voice", tags=["Voice Platform Integration"])


@router.get("/status")
def get_voice_platform_status():
    """Returns current voice platform configuration status without revealing secrets."""
    return {
        "active_platform": settings.VOICE_PLATFORM,
        "retell": {
            "api_key_configured": bool(settings.RETELL_API_KEY and settings.RETELL_API_KEY != "your_retell_api_key_here"),
            "agent_id_configured": bool(settings.RETELL_AGENT_ID and settings.RETELL_AGENT_ID != "your_retell_agent_id_here"),
            "webhook_secret_configured": bool(settings.RETELL_WEBHOOK_SECRET and settings.RETELL_WEBHOOK_SECRET != "your_retell_webhook_secret_here"),
        },
        "bolna": {
            "api_key_configured": bool(settings.BOLNA_API_KEY and settings.BOLNA_API_KEY != "your_bolna_api_key_here"),
            "agent_id_configured": bool(settings.BOLNA_AGENT_ID and settings.BOLNA_AGENT_ID != "your_bolna_agent_id_here"),
        },
    }


@router.get("/export/retell")
def export_retell_agent():
    """Exports copy-ready Retell AI agent creation schema."""
    return retell_adapter.export_agent_config()


@router.get("/export/bolna")
def export_bolna_agent():
    """Exports copy-ready Bolna agent configuration."""
    return bolna_adapter.export_agent_config()


@router.post("/webhook/retell", response_model=WebhookResponse)
async def handle_retell_webhook(
    request: Request,
    x_retell_signature: Optional[str] = Header(None, alias="X-Retell-Signature"),
):
    """
    Receives Retell AI call lifecycle events (call_started, call_ended, call_analyzed).
    Verifies cryptographic signature if webhook secret is configured.
    """
    body_bytes = await request.body()

    # If secret is configured in production, enforce strict signature verification
    if settings.RETELL_WEBHOOK_SECRET and settings.RETELL_WEBHOOK_SECRET != "your_retell_webhook_secret_here":
        if not WebhookVerifier.verify_retell_signature(body_bytes, x_retell_signature, settings.RETELL_WEBHOOK_SECRET):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing webhook signature.",
            )

    try:
        payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body in webhook payload.")

    event_type = payload.get("event", "unknown_event")
    metadata = retell_adapter.process_webhook_event(event_type, payload)

    return WebhookResponse(
        status="success",
        message=f"Retell event '{event_type}' processed.",
        session_id=metadata.call_id,
        outcome=metadata.outcome,
    )


@router.post("/webhook/bolna", response_model=WebhookResponse)
async def handle_bolna_webhook(request: Request):
    """Receives Bolna call completion events."""
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    event_type = payload.get("status", "event")
    metadata = bolna_adapter.process_webhook_event(event_type, payload)

    return WebhookResponse(
        status="success",
        message=f"Bolna event '{event_type}' processed.",
        session_id=metadata.call_id,
        outcome=metadata.outcome,
    )
