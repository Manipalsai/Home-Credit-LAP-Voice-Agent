import os
from typing import Dict, Any, Optional
from backend.app.voice.adapter_base import VoicePlatformAdapter, CallMetadata
from backend.app.config import settings


class RetellAdapter(VoicePlatformAdapter):
    """Retell AI voice provider integration adapter."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.RETELL_API_KEY
        self.agent_id = settings.RETELL_AGENT_ID

    def get_provider_name(self) -> str:
        return "Retell AI"

    def export_agent_config(self) -> Dict[str, Any]:
        """
        Generates production agent configuration schema matching Retell AI Agent API:
        https://docs.retellai.com/api-references/create-agent
        """
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts", "home_credit_lap_system_prompt.txt")
        norm_path = os.path.abspath(prompt_path)
        system_prompt = ""
        if os.path.exists(norm_path):
            with open(norm_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()

        return {
            "agent_name": f"{settings.COMPANY_NAME} LAP Qualification Agent",
            "voice_id": "11labs-Pooja",  # Indian English/Hindi professional female voice
            "voice_temperature": 0.7,
            "voice_speed": 1.0,
            "volume": 1.0,
            "responsiveness": 0.9,
            "interruption_sensitivity": 0.8,
            "enable_backchannel": True,
            "ambient_sound": "call-center",
            "ambient_sound_volume": 0.1,
            "language": "en-IN",
            "general_prompt": system_prompt,
            "begin_message": f"Hello, am I speaking with {{{{customer_name}}}}?",
            "dynamic_variables": [
                "company_name",
                "customer_name",
                "agent_name",
                "agent_gender",
                "current_date",
                "current_day",
                "current_time",
                "additional_context_from_rag",
                "language_to_speak",
            ],
            "webhook_url": f"https://your-domain.com/api/voice/webhook/retell",
        }

    def process_webhook_event(self, event_type: str, payload: Dict[str, Any]) -> CallMetadata:
        call_obj = payload.get("call", {})
        call_id = call_obj.get("call_id", "unknown_call")
        status = call_obj.get("call_status", event_type)
        transcript = call_obj.get("transcript")
        recording_url = call_obj.get("recording_url")
        analysis = call_obj.get("call_analysis", {})
        custom_vars = call_obj.get("custom_variables", {})

        return CallMetadata(
            call_id=call_id,
            provider="retell",
            status=status,
            customer_phone=custom_vars.get("customer_phone"),
            transcript=transcript,
            recording_url=recording_url,
            outcome=analysis.get("call_summary") or status,
            duration_seconds=call_obj.get("duration_ms", 0) // 1000 if call_obj.get("duration_ms") else None,
        )


retell_adapter = RetellAdapter()
