from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class RetellCallData(BaseModel):
    call_id: str
    agent_id: Optional[str] = None
    call_status: Optional[str] = None
    transcript: Optional[str] = None
    recording_url: Optional[str] = None
    disconnection_reason: Optional[str] = None
    call_analysis: Optional[Dict[str, Any]] = None
    custom_variables: Optional[Dict[str, Any]] = None


class RetellWebhookPayload(BaseModel):
    event: str  # e.g., 'call_started', 'call_ended', 'call_analyzed'
    call: RetellCallData


class BolnaCallPayload(BaseModel):
    agent_id: Optional[str] = None
    call_id: Optional[str] = None
    status: Optional[str] = None
    transcript: Optional[str] = None
    recording_url: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None


class WebhookResponse(BaseModel):
    status: str
    message: str
    session_id: Optional[str] = None
    outcome: Optional[str] = None
