from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from taodock_plugin.models import load_models
from tools.support import HANDLED_ERRORS, api_for, explain_error


class ListModelsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            requested_kind = str(tool_parameters.get("kind") or "media")
            models = load_models(api_for(self.runtime.credentials))
            allowed = (
                {"image", "video"} if requested_kind == "media" else {requested_kind}
            )
            yield self.create_json_message(
                {
                    "models": [
                        {"id": model.id, "kind": model.kind}
                        for model in models
                        if model.kind in allowed
                    ],
                    "guide": "https://docs.taodock.com/en/guide/models.html",
                }
            )
        except HANDLED_ERRORS as error:
            yield self.create_text_message(explain_error(error))
