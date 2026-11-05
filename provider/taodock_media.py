from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from taodock_plugin.api import TaoDockError
from tools.support import api_for, explain_error


class TaoDockMediaProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            api_for(credentials).models()
        except (TaoDockError, ValueError) as error:
            raise ToolProviderCredentialValidationError(explain_error(error)) from error
