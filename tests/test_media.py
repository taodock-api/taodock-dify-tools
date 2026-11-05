import unittest

from taodock_plugin.api import ResponseBytes
from taodock_plugin.media import create_video, generate_image
from taodock_plugin.models import Model


class FakeApi:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def json(self, method, path, *, payload=None, timeout=120):
        self.calls.append((method, path, payload, timeout))
        return self.response

    def bytes(self, path, *, timeout=600):
        self.calls.append(("GET", path, None, timeout))
        return ResponseBytes(b"video", "video/mp4")


class MediaTests(unittest.TestCase):
    def test_image_model_prompt_and_response_format_cannot_be_replaced(self) -> None:
        api = FakeApi({"data": [{"b64_json": "aW1hZ2U="}]})
        model = Model("image-safe", "image", ("image-generation",), "images")

        images = generate_image(
            api,
            model,
            "trusted prompt",
            {
                "model": "different-model",
                "prompt": "different prompt",
                "response_format": "url",
                "size": "1024x1024",
            },
        )

        self.assertEqual(images, [(b"image", "image/png")])
        payload = api.calls[0][2]
        self.assertEqual(payload["model"], "image-safe")
        self.assertEqual(payload["prompt"], "trusted prompt")
        self.assertEqual(payload["response_format"], "b64_json")
        self.assertEqual(payload["size"], "1024x1024")

    def test_gemini_contents_are_built_from_prompt(self) -> None:
        api = FakeApi(
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "inlineData": {
                                        "data": "aW1hZ2U=",
                                        "mimeType": "image/png",
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        )
        model = Model("gemini-image", "image", ("gemini",), "gemini-generate-content")

        generate_image(
            api,
            model,
            "trusted prompt",
            {
                "contents": [{"parts": [{"text": "different prompt"}]}],
                "temperature": 0.2,
            },
        )

        payload = api.calls[0][2]
        self.assertEqual(
            payload["contents"],
            [{"role": "user", "parts": [{"text": "trusted prompt"}]}],
        )
        self.assertEqual(payload["temperature"], 0.2)

    def test_video_model_cannot_be_replaced_by_request_json(self) -> None:
        api = FakeApi({"id": "task-1", "status": "queued"})

        task = create_video(
            api, "video-safe", {"model": "different-model", "prompt": "hello"}
        )

        self.assertEqual(task["task_id"], "task-1")
        self.assertEqual(api.calls[0][2]["model"], "video-safe")
        self.assertEqual(api.calls[0][2]["prompt"], "hello")


if __name__ == "__main__":
    unittest.main()
