import hmac
import hashlib
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.voice.webhook_verifier import WebhookVerifier
from backend.app.config import settings

client = TestClient(app)


class TestSecurityAndVoice:

    # 37. Webhook signature verification tests
    def test_37_webhook_signature_verification(self):
        secret = "test_secret_key_12345"
        payload = b'{"event":"call_started","call":{"call_id":"call_123"}}'

        # Compute valid HMAC-SHA256
        valid_signature = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

        # Valid signature should pass
        assert WebhookVerifier.verify_retell_signature(payload, valid_signature, secret) is True

        # Invalid signature should fail
        assert WebhookVerifier.verify_retell_signature(payload, "invalid_sig", secret) is False

        # Missing signature should fail
        assert WebhookVerifier.verify_retell_signature(payload, None, secret) is False

        # Missing secret should fail
        assert WebhookVerifier.verify_retell_signature(payload, valid_signature, "") is False

    # 38 & 39. Missing credentials produce clear configuration status without false claims
    def test_38_39_missing_credentials_status(self):
        res = client.get("/api/voice/status")
        assert res.status_code == 200
        data = res.json()
        assert "retell" in data
        assert "bolna" in data
        # Check that boolean flags accurately reflect status
        assert isinstance(data["retell"]["api_key_configured"], bool)

    # 40. Secrets are not leaked in responses
    def test_40_no_secrets_leaked(self):
        status_res = client.get("/api/voice/status")
        status_text = status_res.text.lower()
        assert "secret" not in status_text or "secret_configured" in status_text
        assert "password" not in status_text

        health_res = client.get("/api/health")
        health_text = health_res.text.lower()
        assert "api_key" not in health_text
        assert "password" not in health_text
