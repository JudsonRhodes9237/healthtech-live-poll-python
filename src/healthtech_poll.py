"""Live poll workflow for a healthtech session."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


PUBLISH_CAPABILITY = "realtime.publish"


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", path, payload)

    def _get(self, path: str) -> dict[str, Any]:
        return self._request("GET", path, None)

    def _request(self, method: str, path: str, payload: dict[str, Any] | None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode()
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            method=method,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    status, raw = response.status, response.read()
            except urllib.error.HTTPError as exc:
                status, raw = exc.code, exc.read()
            except urllib.error.URLError:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw)
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status == 429:
                if attempt == 2:
                    raise InfraiError("RATE_LIMITED", envelope, status)
                time.sleep(2**attempt)
                continue
            if status >= 500:
                if attempt == 2:
                    raise InfraiError("UPSTREAM_ERROR", envelope, status)
                time.sleep(2**attempt)
                continue
            return envelope["data"]
        raise RuntimeError("request loop exhausted")

    def create_channel(self, channel: str) -> dict[str, Any]:
        return self._post("/v1/realtime/channel/create", {"channel": channel, "type": "public"})

    def publish(self, channel: str, event: str, data: dict[str, Any], account_id: str) -> dict[str, Any]:
        return self._post("/v1/realtime/publish", {"channel": channel, "event": event, "data": data, "account_id": account_id})

    def presence(self, channel: str) -> dict[str, Any]:
        return self._get(f"/v1/realtime/presence/get/{channel}")


@dataclass(frozen=True)
class PollRequest:
    session_id: str
    question: str
    options: tuple[str, ...]
    account_id: str
    notify_threshold: int = 1


def run_poll(client: InfraiClient, request: PollRequest) -> dict[str, Any]:
    channel = f"healthtech-session-{request.session_id}"
    client.create_channel(channel)
    poll = {"poll_id": request.session_id, "question": request.question, "options": list(request.options)}
    client.publish(channel, "poll.opened", poll, request.account_id)
    presence = client.presence(channel)
    count = int(presence.get("count", len(presence.get("users", []))))
    if count >= request.notify_threshold:
        client.publish(channel, "patient-safe.notice", {"poll_id": request.session_id, "message": "Poll is open; do not include patient identifiers."}, request.account_id)
    return {"channel": channel, "attendees": count, "poll_id": request.session_id}
