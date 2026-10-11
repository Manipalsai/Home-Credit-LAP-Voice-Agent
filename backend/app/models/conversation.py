from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class MessageSender(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class Message(BaseModel):
    id: str
    sender: MessageSender
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimulationTurnRequest(BaseModel):
    session_id: str
    utterance: str
    override_stage: Optional[str] = None


class SimulationTurnResponse(BaseModel):
    session_id: str
    agent_response: str
    is_terminal: bool
    current_stage: str
    outcome: str
    next_question: Optional[str] = None
    extracted_facts: Dict[str, Any] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)


class ConversationSession(BaseModel):
    session_id: str
    customer_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[Message] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
