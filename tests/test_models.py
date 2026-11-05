import unittest

from taodock_plugin.models import classify


class ModelClassificationTests(unittest.TestCase):
    def test_endpoint_capabilities_determine_model_kind(self) -> None:
        models = classify(
            [
                {"id": "image-a", "supported_endpoint_types": ["image-generation"]},
                {"id": "video-a", "supported_endpoint_types": ["openai-video"]},
                {"id": "text-a", "supported_endpoint_types": ["openai"]},
                {"id": "vector-a", "supported_endpoint_types": ["embeddings"]},
            ],
            [],
        )
        self.assertEqual(
            [(model.id, model.kind) for model in models],
            [
                ("image-a", "image"),
                ("video-a", "video"),
                ("text-a", "text"),
                ("vector-a", "embedding"),
            ],
        )

    def test_catalog_identifies_gemini_image_model(self) -> None:
        models = classify(
            [
                {"id": "gemini-image", "supported_endpoint_types": ["gemini"]},
                {"id": "gemini-text", "supported_endpoint_types": ["gemini"]},
            ],
            [
                {
                    "model_name": "gemini-image",
                    "supported_endpoint_types": ["gemini"],
                    "media_options": {"image": {}},
                }
            ],
        )
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].id, "gemini-image")
        self.assertEqual(models[0].kind, "image")
        self.assertEqual(models[0].image_route, "gemini-generate-content")

    def test_explicit_private_model_metadata_is_supported(self) -> None:
        models = classify(
            [
                {
                    "id": "private-image",
                    "kind": "image",
                    "image_route": "images",
                    "supported_endpoint_types": [],
                }
            ],
            None,
        )
        self.assertEqual(models[0].image_route, "images")


if __name__ == "__main__":
    unittest.main()
