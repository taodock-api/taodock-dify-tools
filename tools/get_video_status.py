from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from taodock_plugin.media import get_video
from tools.support import HANDLED_ERRORS, api_for, explain_error


class GetVideoStatusTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            task_id = str(tool_parameters.get("task_id") or "").strip()
            if not task_id:
                raise ValueError("Task ID is required")
            yield self.create_json_message(
                get_video(api_for(self.runtime.credentials), task_id)
            )
        except HANDLED_ERRORS as error:
            yield self.create_text_message(explain_error(error))
