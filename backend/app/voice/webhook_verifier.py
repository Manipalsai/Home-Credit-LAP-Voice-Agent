import hmac
import hashlib
from typing import Optional


class WebhookVerifier:
    """Verifies cryptographic signatures for incoming voice provider webhooks."""

    @staticmethod
    def verify_retell_signature(raw_body: bytes, signature_header: Optional[str], secret: str) -> bool:
        """
        Verifies Retell AI webhook HMAC signature if a secret is configured.
        If no secret is set in the environment, returns False unless explicitly bypassed in dev.
        """
        if not secret:
            # Secret is missing in config: fail securely
            return False

        if not signature_header:
            return False

        try:
            expected_signature = hmac.new(
                secret.encode("utf-8"),
                raw_body,
                hashlib.sha256
            ).hexdigest()

            # Compare signatures in constant time to prevent timing attacks
            return hmac.compare_digest(expected_signature, signature_header.strip())
        except Exception:
            return False
