from __future__ import annotations

import json
from typing import Any

from taodock_plugin.api import TaoDockApi, TaoDockError

HANDLED_ERRORS = (TaoDockError, TypeError, ValueError)


def api_for(credentials: dict[str, Any]) -> TaoDockApi:
    value = credentials.get("api_key")
    return TaoDockApi(value if isinstance(value, str) else "")


def object_parameter(value: Any, label: str) -> dict[str, Any]:
    if value is None or value == "":
        return {}
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a JSON object")
    try:
        parsed = json.loads(value)
    except ValueError as error:
        raise ValueError(f"{label} must be valid JSON") from error
    if not isinstance(parsed, dict):
        raise TypeError(f"{label} must be a JSON object")
    return parsed


def explain_error(error: Exception) -> str:
    if not isinstance(error, TaoDockError):
        return str(error)
    suffix = f" Request ID: {error.request_id}." if error.request_id else ""
    if error.kind == "unauthorized":
        return f"The TaoDock API key is missing, invalid, expired, or disabled. Check https://taodock.com/keys.{suffix}"
    if error.kind == "insufficient_quota":
        return f"The TaoDock balance or key quota is insufficient. Check https://taodock.com/wallet.{suffix}"
    if error.kind == "model_not_found":
        return f"This key cannot use the selected model. Check https://taodock.com/models.{suffix}"
    if error.kind == "rate_limited":
        return f"TaoDock rate limit reached. Try again later.{suffix}"
    if error.kind == "timeout":
        return f"The TaoDock request timed out. Try again later.{suffix}"
    if error.kind == "network":
        return f"Could not connect to TaoDock. Check the Dify network configuration.{suffix}"
    return f"{error}{suffix}"
