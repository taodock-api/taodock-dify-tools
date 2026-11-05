import unittest
from pathlib import Path

import yaml

from taodock_plugin import VERSION


class MetadataTests(unittest.TestCase):
    def test_manifest_and_python_version_match(self) -> None:
        manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], VERSION)
        self.assertEqual(manifest["author"], "taodock-api")
        self.assertEqual(
            manifest["repo"], "https://github.com/taodock-api/taodock-dify-tools"
        )

    def test_provider_registers_all_tool_descriptors(self) -> None:
        provider = yaml.safe_load(
            Path("provider/taodock_media.yaml").read_text(encoding="utf-8")
        )
        for descriptor in provider["tools"]:
            self.assertTrue(Path(descriptor).is_file(), descriptor)


if __name__ == "__main__":
    unittest.main()
