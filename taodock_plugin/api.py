from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from taodock_plugin import VERSION

API_ROOT = "https://taodock.com/v1"
CATALOG_URL = "https://taodock.com/api/pricing"


@dataclass(frozen=True, slots=True)
class ResponseBytes:
    content: bytes
    content_type: str | None


class TaoDockError(RuntimeError):
    def __init__(
        self,
        kind: str,
        message: str,
        *,
        status: int | None = None,
        code: str | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.kind = kind
        self.status = status
        self.code = code
        self.request_id = request_id


def _failure_kind(status: int, code: str | None) -> str:
    if status == 401:
        return "unauthorized"
    if code == "insufficient_user_quota":
        return "insufficient_quota"
    if code == "model_not_found":
        return "model_not_found"
    if code == "unsupported_endpoint":
        return "unsupported_endpoint"
    if status == 429 or code == "rate_limit_exceeded":
        return "rate_limited"
    return "service"


def _decode_error(error: HTTPError) -> TaoDockError:
    raw = error.read()
    message = error.reason or f"HTTP {error.code}"
    code: str | None = None
    try:
        body = json.loads(raw.decode("utf-8"))
        detail = body.get("error") if isinstance(body, dict) else None
        if isinstance(detail, dict):
            if isinstance(detail.get("message"), str):
                message = detail["message"]
            if isinstance(detail.get("code"), str):
                code = detail["code"]
        elif isinstance(body, dict) and isinstance(body.get("message"), str):
            message = body["message"]
    except (UnicodeDecodeError, ValueError):
        pass
    request_id = error.headers.get("x-request-id") if error.headers else None
    return TaoDockError(
        _failure_kind(error.code, code),
        str(message),
        status=error.code,
        code=code,
        request_id=request_id,
    )


class TaoDockApi:
    def __init__(
        self,
        api_key: str,
        *,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        clean_key = api_key.strip()
        if not clean_key:
            raise TaoDockError("unauthorized", "A TaoDock API key is required")
        self._api_key = clean_key
        self._opener = opener

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        timeout: float = 120,
    ) -> ResponseBytes:
        data = (
            None
            if payload is None
            else json.dumps(payload, separators=(",", ":")).encode("utf-8")
        )
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": f"taodock-dify/{VERSION}",
            "X-TaoDock-Plugin": f"taodock-dify/{VERSION}",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = Request(
            f"{API_ROOT}/{path.lstrip('/')}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with self._opener(request, timeout=timeout) as response:
                return ResponseBytes(
                    response.read(), response.headers.get("content-type")
                )
        except HTTPError as error:
            raise _decode_error(error) from error
        except TimeoutError as error:
            raise TaoDockError("timeout", "The TaoDock request timed out") from error
        except (URLError, OSError) as error:
            raise TaoDockError("network", "Could not connect to TaoDock") from error

    def json(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        timeout: float = 120,
    ) -> dict[str, Any]:
        response = self._request(method, path, payload=payload, timeout=timeout)
        try:
            body = json.loads(response.content.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as error:
            raise TaoDockError("service", "TaoDock returned invalid JSON") from error
        if not isinstance(body, dict):
            raise TaoDockError("service", "TaoDock returned an unexpected response")
        return body

    def bytes(self, path: str, *, timeout: float = 600) -> ResponseBytes:
        return self._request("GET", path, timeout=timeout)

    def models(self) -> list[dict[str, Any]]:
        data = self.json("GET", "models?scope=authorized").get("data")
        return (
            [item for item in data if isinstance(item, dict)]
            if isinstance(data, list)
            else []
        )


def public_json(
    url: str,
    *,
    opener: Callable[..., Any] = urlopen,
    timeout: float = 8,
) -> dict[str, Any]:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "taodock.com":
        raise ValueError("Only TaoDock HTTPS URLs are allowed")
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": f"taodock-dify/{VERSION}"},
    )
    try:
        with opener(request, timeout=timeout) as response:
            value = json.loads(response.read().decode("utf-8"))
    except (
        HTTPError,
        URLError,
        TimeoutError,
        OSError,
        UnicodeDecodeError,
        ValueError,
    ) as error:
        raise TaoDockError(
            "network", "Could not read the TaoDock model catalog"
        ) from error
    if not isinstance(value, dict):
        raise TaoDockError("service", "TaoDock returned an unexpected catalog response")
    return value
