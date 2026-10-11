import os
from typing import Dict, Any, Optional
from backend.app.voice.adapter_base import VoicePlatformAdapter, CallMetadata
from backend.app.config import settings


class BolnaAdapter(VoicePlatformAdapter):
    """Bolna voice platform integration adapter."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.BOLNA_API_KEY
        self.agent_id = settings.BOLNA_AGENT_ID

    def get_provider_name(self) -> str:
        return "Bolna"

    def export_agent_config(self) -> Dict[str, Any]:
        """Exports agent configuration matching Bolna API structure."""
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts", "home_credit_lap_system_prompt.txt")
        norm_path = os.path.abspath(prompt_path)
        system_prompt = ""
        if os.path.exists(norm_path):
            with open(norm_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()

        return {
            "agent_name": f"{settings.COMPANY_NAME} LAP Bolna Agent",
            "agent_type": "telephony",
            "voice": "polly-aditi",  # Indian English/Hindi voice
            "system_prompt": system_prompt,
            "tasks": [
                {
                    "task_type": "conversation",
                    "tools_config": {},
                    "llm_config": {
                        "model": "gpt-4o-mini",
                        "max_tokens": 150,
                    },
                }
            ],
            "webhook": f"https://your-domain.com/api/voice/webhook/bolna",
        }

    def process_webhook_event(self, event_type: str, payload: Dict[str, Any]) -> CallMetadata:
        call_id = payload.get("call_id", "unknown_bolna_call")
        status = payload.get("status", event_type)
        transcript = payload.get("transcript")
        recording_url = payload.get("recording_url")
        extracted = payload.get("extracted_data", {})

        return CallMetadata(
            call_id=call_id,
            provider="bolna",
            status=status,
            transcript=transcript,
            recording_url=recording_url,
            outcome=str(extracted.get("outcome", status)),
        )


bolna_adapter = BolnaAdapter()
