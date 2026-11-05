import json
import unittest

from taodock_plugin.api import TaoDockApi, TaoDockError


class FakeResponse:
    def __init__(self, body: dict, content_type: str = "application/json") -> None:
        self._body = json.dumps(body).encode()
        self.headers = {"content-type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return self._body


class ApiTests(unittest.TestCase):
    def test_key_is_required(self) -> None:
        with self.assertRaises(TaoDockError):
            TaoDockApi("  ")

    def test_request_uses_taodock_identity_and_bearer_key(self) -> None:
        captured = {}

        def opener(request, *, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return FakeResponse({"data": [{"id": "model-a"}]})

        models = TaoDockApi("secret-value", opener=opener).models()

        self.assertEqual(models, [{"id": "model-a"}])
        request = captured["request"]
        self.assertEqual(
            request.full_url, "https://taodock.com/v1/models?scope=authorized"
        )
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-value")
        self.assertEqual(request.get_header("X-taodock-plugin"), "taodock-dify/0.2.0")
        self.assertEqual(captured["timeout"], 120)


if __name__ == "__main__":
    unittest.main()
