from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from taodock_plugin.media import create_video, download_video, wait_for_video
from taodock_plugin.models import require_model
from tools.support import HANDLED_ERRORS, api_for, explain_error, object_parameter


class GenerateVideoTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            api = api_for(self.runtime.credentials)
            model_id = str(tool_parameters.get("model") or "").strip()
            model = require_model(api, model_id, "video")
            task = create_video(
                api,
                model.id,
                object_parameter(tool_parameters.get("request"), "Request"),
            )
            wait_seconds = max(
                0.0, min(float(tool_parameters.get("wait_seconds") or 0), 540.0)
            )
            if wait_seconds:
                task = wait_for_video(api, task["task_id"], wait_seconds)
            if task["status"] == "failed":
                detail = task.get("error")
                message = (
                    detail.get("message")
                    if isinstance(detail, dict)
                    else "generation failed"
                )
                raise ValueError(f"Video task {task['task_id']} failed: {message}")
            if task["status"] != "completed":
                yield self.create_json_message(task)
                return
            result = download_video(api, task["task_id"])
            yield self.create_blob_message(
                blob=result.content,
                meta={"mime_type": result.content_type or "video/mp4"},
            )
        except HANDLED_ERRORS as error:
            yield self.create_text_message(explain_error(error))
