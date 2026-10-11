from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


class TestAPI:

    def test_health_endpoint(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "features" in data

    def test_conversation_lifecycle_api(self):
        # Start
        start_res = client.post("/api/conversation/start", json={"customer_name": "Siddharth"})
        assert start_res.status_code == 200
        start_data = start_res.json()
        session_id = start_data["session_id"]
        assert "Hello, am I speaking with Siddharth?" in start_data["greeting"]

        # Turn
        turn_res = client.post(
            "/api/conversation/turn",
            json={"session_id": session_id, "utterance": "Yes, Siddharth speaking."},
        )
        assert turn_res.status_code == 200
        turn_data = turn_res.json()
        assert turn_data["current_stage"] == "offer_presentation"

        # Get State
        get_res = client.get(f"/api/conversation/{session_id}")
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert len(get_data["messages"]) >= 2

        # Reset
        reset_res = client.post("/api/conversation/reset", json={"session_id": session_id})
        assert reset_res.status_code == 200
        assert reset_res.json()["status"] == "reset_successful"

    def test_empty_turn_utterance_rejected(self):
        res = client.post("/api/conversation/turn", json={"session_id": "test_err", "utterance": ""})
        assert res.status_code == 400

    def test_rendered_prompt_endpoint(self):
        start_res = client.post("/api/conversation/start", json={"customer_name": "Pooja"})
        session_id = start_res.json()["session_id"]
        res = client.get(f"/api/conversation/{session_id}/prompt")
        assert res.status_code == 200
        assert "Home Credit India" in res.json()["rendered_prompt"]

    def test_simulator_endpoints(self):
        list_res = client.get("/api/simulator/scenarios")
        assert list_res.status_code == 200
        scenarios = list_res.json()
        assert len(scenarios) > 0

        # Run one scenario
        first_id = scenarios[0]["id"]
        run_res = client.post("/api/simulator/run", json={"scenario_id": first_id})
        assert run_res.status_code == 200
        assert run_res.json()["passed"] is True

    def test_voice_export_endpoints(self):
        retell_exp = client.get("/api/voice/export/retell")
        assert retell_exp.status_code == 200
        assert "voice_id" in retell_exp.json()

        bolna_exp = client.get("/api/voice/export/bolna")
        assert bolna_exp.status_code == 200
        assert "agent_type" in bolna_exp.json()
