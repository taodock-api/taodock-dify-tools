from __future__ import annotations

import base64
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import quote

from taodock_plugin.api import ResponseBytes, TaoDockApi, TaoDockError
from taodock_plugin.models import Model


def _openai_images(body: dict[str, Any]) -> list[tuple[bytes, str]]:
    output: list[tuple[bytes, str]] = []
    data = body.get("data")
    if not isinstance(data, list):
        return output
    for item in data:
        encoded = item.get("b64_json") if isinstance(item, dict) else None
        if not isinstance(encoded, str) or not encoded:
            continue
        try:
            output.append((base64.b64decode(encoded, validate=True), "image/png"))
        except ValueError:
            continue
    return output


def _gemini_images(body: dict[str, Any]) -> list[tuple[bytes, str]]:
    output: list[tuple[bytes, str]] = []
    candidates = body.get("candidates")
    if not isinstance(candidates, list):
        return output
    for candidate in candidates:
        content = candidate.get("content") if isinstance(candidate, dict) else None
        parts = content.get("parts") if isinstance(content, dict) else None
        if not isinstance(parts, list):
            continue
        for part in parts:
            if not isinstance(part, dict):
                continue
            inline = part.get("inlineData") or part.get("inline_data")
            if not isinstance(inline, dict) or not isinstance(inline.get("data"), str):
                continue
            try:
                data = base64.b64decode(inline["data"], validate=True)
            except ValueError:
                continue
            mime_type = inline.get("mimeType") or inline.get("mime_type") or "image/png"
            output.append((data, str(mime_type)))
    return output


def generate_image(
    api: TaoDockApi,
    model: Model,
    prompt: str,
    settings: dict[str, Any],
    *,
    edit: bool = False,
) -> list[tuple[bytes, str]]:
    if model.kind != "image" or not model.image_route:
        raise ValueError(f"{model.id} is not an image model")
    if edit and model.image_route != "images":
        raise ValueError(f"{model.id} does not support image edit mode")

    if model.image_route == "gemini-generate-content":
        safe_settings = {
            key: value
            for key, value in settings.items()
            if key not in {"model", "contents"}
        }
        body = api.json(
            "POST",
            f"models/{quote(model.id, safe='')}:generateContent",
            payload={
                **safe_settings,
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            },
        )
        images = _gemini_images(body)
    else:
        safe_settings = {
            key: value
            for key, value in settings.items()
            if key not in {"model", "prompt", "response_format"}
        }
        body = api.json(
            "POST",
            "images/edits" if edit else "images/generations",
            payload={
                **safe_settings,
                "model": model.id,
                "prompt": prompt,
                "response_format": "b64_json",
            },
        )
        images = _openai_images(body)

    if not images:
        raise TaoDockError("service", f"{model.id} returned no image data")
    return images


def _task(body: dict[str, Any]) -> dict[str, Any]:
    task_id = body.get("id") or body.get("task_id")
    if not isinstance(task_id, str) or not task_id:
        raise TaoDockError("service", "TaoDock returned a video task without an ID")
    return {
        "task_id": task_id,
        "status": body.get("status") or "queued",
        **({"model": body["model"]} if isinstance(body.get("model"), str) else {}),
        **(
            {"progress": body["progress"]}
            if isinstance(body.get("progress"), (int, float))
            else {}
        ),
        **({"error": body["error"]} if isinstance(body.get("error"), dict) else {}),
    }


def create_video(
    api: TaoDockApi, model_id: str, request: dict[str, Any]
) -> dict[str, Any]:
    safe_request = {key: value for key, value in request.items() if key != "model"}
    return _task(
        api.json("POST", "videos", payload={**safe_request, "model": model_id})
    )


def get_video(api: TaoDockApi, task_id: str) -> dict[str, Any]:
    return _task(api.json("GET", f"videos/{quote(task_id, safe='')}"))


def wait_for_video(
    api: TaoDockApi,
    task_id: str,
    timeout_seconds: float,
    *,
    interval_seconds: float = 5,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    deadline = monotonic() + max(0, timeout_seconds)
    task = get_video(api, task_id)
    while task["status"] not in {"completed", "failed"} and monotonic() < deadline:
        sleep(min(interval_seconds, max(0, deadline - monotonic())))
        task = get_video(api, task_id)
    return task


def download_video(api: TaoDockApi, task_id: str) -> ResponseBytes:
    return api.bytes(f"videos/{quote(task_id, safe='')}/content", timeout=600)
