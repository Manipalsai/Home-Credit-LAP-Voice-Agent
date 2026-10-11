from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid

from backend.app.services.conversation_service import conversation_service
from backend.app.models.conversation import SimulationTurnRequest, SimulationTurnResponse

router = APIRouter(prefix="/conversation", tags=["Conversation"])


class StartConversationRequest(BaseModel):
    customer_name: Optional[str] = "Rajesh Sharma"
    session_id: Optional[str] = None


class StartConversationResponse(BaseModel):
    session_id: str
    customer_name: str
    greeting: str
    stage: str
    state: Dict[str, Any]


class TurnRequest(BaseModel):
    session_id: str
    utterance: str


class ResetRequest(BaseModel):
    session_id: str
    customer_name: Optional[str] = "Rajesh Sharma"


@router.post("/start", response_model=StartConversationResponse)
def start_conversation(req: StartConversationRequest):
    """Initializes a new conversational qualification session and returns greeting."""
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:8]}"
    state = conversation_service.get_or_create_session(session_id, req.customer_name or "Rajesh Sharma")
    greeting = conversation_service.get_initial_greeting(session_id, state.customer_name)
    return StartConversationResponse(
        session_id=session_id,
        customer_name=state.customer_name,
        greeting=greeting,
        stage=state.stage.value,
        state=state.model_dump(),
    )


@router.post("/turn", response_model=SimulationTurnResponse)
def process_turn(req: TurnRequest):
    """Processes customer utterance, extracts facts, evaluates business rules, and returns agent response."""
    if not req.utterance or not req.utterance.strip():
        raise HTTPException(status_code=400, detail="Customer utterance cannot be empty.")

    agent_response, state, extracted_facts = conversation_service.process_turn(req.session_id, req.utterance)
    return SimulationTurnResponse(
        session_id=state.session_id,
        agent_response=agent_response,
        is_terminal=state.is_terminal,
        current_stage=state.stage.value,
        outcome=state.outcome.value,
        next_question=state.current_prompt,
        extracted_facts=extracted_facts,
        state=state.model_dump(),
    )


@router.get("/{session_id}")
def get_session_state(session_id: str):
    """Retrieves current qualification state and message history."""
    state = conversation_service.get_or_create_session(session_id)
    history = conversation_service.get_history(session_id)
    return {
        "session_id": session_id,
        "state": state.model_dump(),
        "messages": [m.model_dump() for m in (history.messages if history else [])],
    }


@router.post("/reset")
def reset_session(req: ResetRequest):
    """Resets a conversation session to start clean."""
    state = conversation_service.reset_session(req.session_id, req.customer_name or "Rajesh Sharma")
    greeting = conversation_service.get_initial_greeting(req.session_id, state.customer_name)
    return {
        "status": "reset_successful",
        "session_id": req.session_id,
        "greeting": greeting,
        "state": state.model_dump(),
    }


@router.get("/{session_id}/prompt")
def get_rendered_prompt(session_id: str, utterance: Optional[str] = None):
    """Renders the complete System Prompt with all 11 runtime variables for the current session state."""
    rendered_prompt = conversation_service.render_system_prompt(session_id, utterance or "")
    return {
        "session_id": session_id,
        "rendered_prompt": rendered_prompt,
    }
