import glob
import json
import os
import pytest
from backend.app.services.simulator_service import SimulatorService

SCENARIOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scenarios"))


def get_all_scenarios():
    scenarios = []
    files = glob.glob(os.path.join(SCENARIOS_DIR, "*.json"))
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            if isinstance(data, list):
                scenarios.extend(data)
            elif isinstance(data, dict):
                scenarios.append(data)
    return scenarios


all_scenarios = get_all_scenarios()


@pytest.mark.parametrize("scenario", all_scenarios, ids=[s.get("id", s.get("name", "test")) for s in all_scenarios])
def test_simulation_scenario(scenario):
    result = SimulatorService.run_scenario(scenario)
    assert result.passed, f"Scenario '{result.scenario_name}' failed: {result.failure_reason}"
