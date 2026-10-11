import json
import os
import glob
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.simulator_service import SimulatorService, SimulationRunResult

router = APIRouter(prefix="/simulator", tags=["Simulator"])

SCENARIOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scenarios"))


class ScenarioSummary(BaseModel):
    id: str
    name: str
    category: str
    expected_outcome: str
    description: str
    turn_count: int


class RunScenarioRequest(BaseModel):
    scenario_id: Optional[str] = None
    custom_scenario: Optional[Dict[str, Any]] = None


def load_all_scenarios() -> List[Dict[str, Any]]:
    scenarios: List[Dict[str, Any]] = []
    if not os.path.exists(SCENARIOS_DIR):
        return scenarios

    for file_path in glob.glob(os.path.join(SCENARIOS_DIR, "*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                category = os.path.splitext(os.path.basename(file_path))[0]
                if isinstance(data, list):
                    for item in data:
                        item["category"] = category
                        scenarios.append(item)
                elif isinstance(data, dict):
                    data["category"] = category
                    scenarios.append(data)
        except Exception:
            continue
    return scenarios


@router.get("/scenarios", response_model=List[ScenarioSummary])
def list_scenarios():
    """Lists all available simulation test scenarios."""
    scenarios = load_all_scenarios()
    summaries = []
    for s in scenarios:
        summaries.append(
            ScenarioSummary(
                id=s.get("id", s.get("name", "unnamed").lower().replace(" ", "_")),
                name=s.get("name", "Unnamed Scenario"),
                category=s.get("category", "general"),
                expected_outcome=s.get("expected_outcome", "unknown"),
                description=s.get("description", ""),
                turn_count=len(s.get("turns", [])),
            )
        )
    return summaries


@router.post("/run", response_model=SimulationRunResult)
def run_scenario(req: RunScenarioRequest):
    """Runs a simulated conversation scenario and evaluates pass/fail status."""
    scenario_to_run = None

    if req.custom_scenario:
        scenario_to_run = req.custom_scenario
    elif req.scenario_id:
        all_scenarios = load_all_scenarios()
        for s in all_scenarios:
            curr_id = s.get("id", s.get("name", "").lower().replace(" ", "_"))
            if curr_id == req.scenario_id or s.get("id") == req.scenario_id:
                scenario_to_run = s
                break

    if not scenario_to_run:
        raise HTTPException(status_code=404, detail="Scenario not found or not specified.")

    result = SimulatorService.run_scenario(scenario_to_run)
    return result
