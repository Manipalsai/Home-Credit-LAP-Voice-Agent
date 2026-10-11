import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.app.services.conversation_service import conversation_service
from backend.app.models.qualification import CallOutcome, ConversationStage


class SimulationStepResult(BaseModel):
    turn_index: int
    customer_utterance: str
    agent_response: str
    stage: str
    outcome: str
    is_terminal: bool
    extracted_facts: Dict[str, Any]
    checklist_status: Dict[str, str]


class SimulationRunResult(BaseModel):
    scenario_name: str
    session_id: str
    passed: bool
    expected_outcome: str
    actual_outcome: str
    total_turns: int
    steps: List[SimulationStepResult]
    failure_reason: Optional[str] = None


class SimulatorService:
    """Runs automated multi-turn conversational scenarios against the qualification engine."""

    @staticmethod
    def run_scenario(scenario_data: Dict[str, Any]) -> SimulationRunResult:
        scenario_name = scenario_data.get("name", "Unnamed Scenario")
        customer_name = scenario_data.get("customer_name", "Rajesh Sharma")
        expected_outcome = scenario_data.get("expected_outcome", "")
        turns: List[str] = scenario_data.get("turns", [])

        session_id = f"sim_{uuid.uuid4().hex[:8]}"
        conversation_service.reset_session(session_id, customer_name)

        steps: List[SimulationStepResult] = []
        final_state = None

        for idx, turn in enumerate(turns):
            agent_response, state, facts = conversation_service.process_turn(session_id, turn)
            final_state = state

            # snapshot checklist
            checklist_snapshot = {
                key.value: item.state.value for key, item in state.checklist.items()
            }

            steps.append(
                SimulationStepResult(
                    turn_index=idx + 1,
                    customer_utterance=turn,
                    agent_response=agent_response,
                    stage=state.stage.value,
                    outcome=state.outcome.value,
                    is_terminal=state.is_terminal,
                    extracted_facts=facts,
                    checklist_status=checklist_snapshot,
                )
            )

            if state.is_terminal:
                break

        actual_outcome = final_state.outcome.value if final_state else CallOutcome.IN_PROGRESS.value
        passed = (actual_outcome == expected_outcome)

        failure_reason = None
        if not passed:
            failure_reason = f"Expected outcome '{expected_outcome}', but got '{actual_outcome}'."

        return SimulationRunResult(
            scenario_name=scenario_name,
            session_id=session_id,
            passed=passed,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome,
            total_turns=len(steps),
            steps=steps,
            failure_reason=failure_reason,
        )
