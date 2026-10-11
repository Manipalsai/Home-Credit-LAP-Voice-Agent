from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class CallMetadata(BaseModel):
    call_id: str
    provider: str
    status: str
    customer_phone: Optional[str] = None
    transcript: Optional[str] = None
    recording_url: Optional[str] = None
    outcome: Optional[str] = None
    duration_seconds: Optional[int] = None


class VoicePlatformAdapter(ABC):
    """Abstract interface for Voice Telephony Platforms (Retell AI, Bolna, etc.)."""

    @abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abstractmethod
    def export_agent_config(self) -> Dict[str, Any]:
        """Exports agent configuration json ready to create/update agent on provider API."""
        pass

    @abstractmethod
    def process_webhook_event(self, event_type: str, payload: Dict[str, Any]) -> CallMetadata:
        pass
