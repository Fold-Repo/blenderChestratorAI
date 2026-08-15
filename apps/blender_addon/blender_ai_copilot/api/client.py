"""Backend API client for authenticated Blender-to-backend communication."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib import error, request


class BackendClientError(Exception):
    pass


@dataclass
class BackendClient:
    base_url: str
    timeout_seconds: float = 4.0
    retry_attempts: int = 1
    auth_token: str | None = None

    @staticmethod
    def _request_id() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _build_url(self, path: str) -> str:
        normalized_base = self.base_url.rstrip("/")
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{normalized_base}{normalized_path}"

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-request-id": self._request_id(),
        }

        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        last_error: Exception | None = None
        total_attempts = max(1, self.retry_attempts + 1)

        for _attempt in range(total_attempts):
            req = request.Request(
                self._build_url(path),
                data=body,
                headers=headers,
                method=method,
            )

            try:
                with request.urlopen(req, timeout=self.timeout_seconds) as response:
                    raw = response.read().decode("utf-8")
                    return json.loads(raw) if raw else {}
            except error.HTTPError as exc:
                raw = exc.read().decode("utf-8") if exc.fp else ""
                try:
                    parsed = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    parsed = {}

                api_message = parsed.get("error", {}).get("message")
                raise BackendClientError(
                    api_message or f"Backend request failed with status {exc.code}."
                ) from exc
            except (error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
                last_error = exc

        raise BackendClientError(
            f"Unable to reach backend at {self.base_url}: {last_error}"
        )

    def health(self) -> dict[str, Any]:
        return self._request_json("GET", "/api/v1/health")

    def register(self, username: str, email: str, password: str) -> dict[str, Any]:
        return self._request_json(
            "POST",
            "/api/v1/auth/register",
            {"username": username, "email": email, "password": password},
        )

    def login(self, username: str, password: str) -> dict[str, Any]:
        return self._request_json(
            "POST",
            "/api/v1/auth/login",
            {"username": username, "password": password},
        )

    def create_project(self, name: str) -> dict[str, Any]:
        response = self._request_json("POST", "/api/v1/projects", {"name": name})
        return response.get("project", {})

    def create_conversation(self, project_id: str) -> dict[str, Any]:
        response = self._request_json(
            "POST", f"/api/v1/projects/{project_id}/conversations", {}
        )
        return response.get("conversation", {})

    def create_run(
        self,
        conversation_id: str,
        message: str,
        scene_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"message": message}
        if scene_context is not None:
            payload["scene_context"] = scene_context

        response = self._request_json(
            "POST",
            f"/api/v1/conversations/{conversation_id}/runs",
            payload,
        )
        return response.get("run", {})

    def create_audit_log(
        self,
        project_id: str,
        action: str,
        tool: str | None = None,
        parameters_metadata: dict[str, Any] | None = None,
        approval_required: bool = False,
        approved: bool = False,
        execution_result: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "projectId": project_id,
            "action": action,
            "tool": tool,
            "parametersMetadata": parameters_metadata,
            "approvalRequired": approval_required,
            "approved": approved,
            "executionResult": execution_result,
        }
        return self._request_json("POST", "/api/v1/audit-logs", payload)
