from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from taodock_plugin.api import CATALOG_URL, TaoDockApi, TaoDockError, public_json


@dataclass(frozen=True, slots=True)
class Model:
    id: str
    kind: str
    endpoints: tuple[str, ...]
    image_route: str | None = None


_TEXT_ENDPOINTS = frozenset(
    {"openai", "openai-response", "openai-response-compact", "anthropic"}
)
_KINDS = frozenset({"text", "image", "video", "embedding", "rerank"})


def _has_price(points: Any) -> bool:
    if not isinstance(points, list):
        return False
    return any(
        isinstance(point, dict)
        and isinstance(point.get("price"), (int, float))
        and point["price"] > 0
        for point in points
    )


def _image_catalog_entry(entry: dict[str, Any] | None) -> bool:
    if not entry:
        return False
    media = entry.get("media_options")
    if isinstance(media, dict) and media.get("image") is not None:
        return True
    generation = entry.get("image_generation_prices")
    if isinstance(generation, list):
        for point in generation:
            if (
                isinstance(point, dict)
                and isinstance(point.get("size"), str)
                and point["size"]
                and isinstance(point.get("price"), (int, float))
                and point["price"] > 0
            ):
                return True
    return _has_price(entry.get("image_feature_prices"))


def _video_catalog_entry(entry: dict[str, Any] | None) -> bool:
    if not entry:
        return False
    media = entry.get("media_options")
    if isinstance(media, dict) and media.get("video") is not None:
        return True
    prices = entry.get("video_resolution_price")
    if isinstance(prices, dict) and any(
        isinstance(value, (int, float)) and value > 0 for value in prices.values()
    ):
        return True
    return _has_price(entry.get("video_feature_prices"))


def _image_route(endpoints: set[str], declared: Any = None) -> str | None:
    if declared in {"images", "gemini-generate-content"}:
        return declared
    if "gemini" in endpoints:
        return "gemini-generate-content"
    if "image-generation" in endpoints:
        return "images"
    return None


def classify(
    available: list[dict[str, Any]], catalog: list[dict[str, Any]] | None
) -> list[Model]:
    catalog_by_id = {
        entry["model_name"]: entry
        for entry in catalog or []
        if isinstance(entry, dict) and isinstance(entry.get("model_name"), str)
    }
    result: list[Model] = []

    for item in available:
        model_id = item.get("id")
        if not isinstance(model_id, str) or not model_id:
            continue
        catalog_item = catalog_by_id.get(model_id)
        own = item.get("supported_endpoint_types")
        catalog_endpoints = (
            catalog_item.get("supported_endpoint_types") if catalog_item else None
        )
        own_values = (
            [value for value in own if isinstance(value, str)]
            if isinstance(own, list)
            else []
        )
        catalog_values = (
            [value for value in catalog_endpoints if isinstance(value, str)]
            if isinstance(catalog_endpoints, list)
            else []
        )
        endpoints = tuple(dict.fromkeys([*own_values, *catalog_values]))
        endpoint_set = set(endpoints)
        declared_kind = item.get("kind")

        if declared_kind in _KINDS:
            route = (
                _image_route(endpoint_set, item.get("image_route"))
                if declared_kind == "image"
                else None
            )
            if declared_kind != "image" or route:
                result.append(Model(model_id, declared_kind, endpoints, route))
            continue
        if "openai-video" in endpoint_set or _video_catalog_entry(catalog_item):
            result.append(Model(model_id, "video", endpoints))
            continue
        if "image-generation" in endpoint_set or _image_catalog_entry(catalog_item):
            route = _image_route(endpoint_set)
            if route:
                result.append(Model(model_id, "image", endpoints, route))
            continue
        if "embeddings" in endpoint_set:
            result.append(Model(model_id, "embedding", endpoints))
            continue
        if "jina-rerank" in endpoint_set:
            result.append(Model(model_id, "rerank", endpoints))
            continue
        if any(endpoint in _TEXT_ENDPOINTS for endpoint in own_values):
            result.append(Model(model_id, "text", endpoints))

    return result


def load_models(
    api: TaoDockApi,
    *,
    catalog_reader: Callable[[], dict[str, Any]] | None = None,
    available: list[dict[str, Any]] | None = None,
) -> list[Model]:
    available_models = api.models() if available is None else available
    reader = catalog_reader or (lambda: public_json(CATALOG_URL))
    try:
        body = reader()
        raw_catalog = body.get("data")
        catalog = (
            [entry for entry in raw_catalog if isinstance(entry, dict)]
            if isinstance(raw_catalog, list)
            else []
        )
    except (TaoDockError, ValueError):
        catalog = None
    return classify(available_models, catalog)


def require_model(api: TaoDockApi, model_id: str, kind: str) -> Model:
    available = api.models()
    listed_ids = {entry.get("id") for entry in available}
    for model in load_models(api, available=available):
        if model.id != model_id:
            continue
        if model.kind != kind:
            raise ValueError(f"{model_id} is a {model.kind} model, not a {kind} model")
        return model
    if model_id in listed_ids:
        raise ValueError(f"Could not determine the media type for {model_id}")
    raise TaoDockError(
        "model_not_found", f"{model_id} is not available to this TaoDock API key"
    )
