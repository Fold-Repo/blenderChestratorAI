import json
import unittest
from unittest.mock import patch

from apps.blender_addon.blender_ai_copilot.api.client import (
    BackendClient,
    BackendClientError,
)


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):  # noqa: ANN001
        return False


class TestBackendClient(unittest.TestCase):
    def test_health_success(self):
        client = BackendClient("http://localhost:3000")

        with patch(
            "apps.blender_addon.blender_ai_copilot.api.client.request.urlopen",
            return_value=_FakeResponse({"status": "ok"}),
        ):
            result = client.health()

        self.assertEqual(result["status"], "ok")

    def test_request_failure_raises_client_error(self):
        client = BackendClient("http://localhost:3000", retry_attempts=0)

        with patch(
            "apps.blender_addon.blender_ai_copilot.api.client.request.urlopen",
            side_effect=ValueError("network error"),
        ):
            with self.assertRaises(BackendClientError):
                client.health()

    def test_sends_bearer_authorization_header(self):
        client = BackendClient("http://localhost:3000", auth_token="token_abc")
        captured = {}

        def fake_urlopen(req, timeout=None):  # noqa: ARG001
            headers = {key.lower(): value for key, value in req.header_items()}
            captured["authorization"] = headers.get("authorization")
            return _FakeResponse({"status": "ok"})

        with patch(
            "apps.blender_addon.blender_ai_copilot.api.client.request.urlopen",
            side_effect=fake_urlopen,
        ):
            client.health()

        self.assertEqual(captured["authorization"], "Bearer token_abc")

    def test_login_and_register_payloads(self):
        client = BackendClient("http://localhost:3000")
        captured = {}

        def fake_urlopen(req, timeout=None):  # noqa: ARG001
            captured["url"] = req.full_url
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return _FakeResponse({"token": "token_1", "user": {"id": "user_1"}})

        with patch(
            "apps.blender_addon.blender_ai_copilot.api.client.request.urlopen",
            side_effect=fake_urlopen,
        ):
            login = client.login("ada", "secret")
            register = client.register("ada", "ada@example.com", "secret")

        self.assertEqual(login["token"], "token_1")
        self.assertEqual(register["token"], "token_1")
        self.assertIn("/api/v1/auth/register", captured["url"])
        self.assertEqual(captured["body"]["email"], "ada@example.com")

    def test_create_audit_log_payload(self):
        client = BackendClient("http://localhost:3000", auth_token="token_abc")
        captured = {}

        def fake_urlopen(req, timeout=None):  # noqa: ARG001
            captured["url"] = req.full_url
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return _FakeResponse({"auditLog": {"id": "audit_1"}})

        with patch(
            "apps.blender_addon.blender_ai_copilot.api.client.request.urlopen",
            side_effect=fake_urlopen,
        ):
            result = client.create_audit_log(
                project_id="proj_1",
                action="preview",
                tool="modify_object_transform",
                approved=False,
                execution_result="success",
            )

        self.assertEqual(result["auditLog"]["id"], "audit_1")
        self.assertEqual(captured["body"]["projectId"], "proj_1")
        self.assertEqual(captured["body"]["action"], "preview")


if __name__ == "__main__":
    unittest.main()
