from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from taodock_plugin.media import generate_image
from taodock_plugin.models import require_model
from tools.support import HANDLED_ERRORS, api_for, explain_error, object_parameter


class GenerateImageTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            api = api_for(self.runtime.credentials)
            model_id = str(tool_parameters.get("model") or "").strip()
            prompt = str(tool_parameters.get("prompt") or "").strip()
            if not prompt:
                raise ValueError("Prompt is required")
            model = require_model(api, model_id, "image")
            images = generate_image(
                api,
                model,
                prompt,
                object_parameter(tool_parameters.get("settings"), "Settings"),
                edit=bool(tool_parameters.get("edit")),
            )
            for content, mime_type in images:
                yield self.create_blob_message(
                    blob=content, meta={"mime_type": mime_type}
                )
        except HANDLED_ERRORS as error:
            yield self.create_text_message(explain_error(error))
