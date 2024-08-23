import os
import json
import toml
import unittest


class TestSemanticRelease(unittest.TestCase):

    def test_package_json_exists(self):
        self.assertTrue(
            os.path.exists(
                os.path.join(os.path.dirname(__file__), "../package.json")
            ),
            "package.json does not exist",
        )

    def test_pyproject_toml_exists(self):
        self.assertTrue(
            os.path.exists(
                os.path.join(os.path.dirname(__file__), "../pyproject.toml")
            ),
            "pyproject.toml does not exist",
        )

    def test_package_json_version(self):
        with open("package.json", "r") as f:
            data = json.load(f)
            self.assertIn(
                "version", data, "version key not found in package.json"
            )
            self.assertRegex(
                data["version"],
                r"^\d+\.\d+\.\d+$",
                "version format in package.json is incorrect",
            )

    def test_pyproject_toml_version(self):
        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
            self.assertIn(
                "tool", data, "tool section not found in pyproject.toml"
            )
            self.assertIn(
                "semantic_release",
                data["tool"],
                "semantic_release section not found in pyproject.toml",
            )
            self.assertIn(
                "version_variable",
                data["tool"]["semantic_release"],
                "version_variable key not found in pyproject.toml",
            )
            self.assertIsInstance(
                data["tool"]["semantic_release"]["version_variable"],
                list,
                "version_variable should be a list",
            )
            self.assertGreater(
                len(data["tool"]["semantic_release"]["version_variable"]),
                0,
                "version_variable list is empty",
            )
            version_variable = data["tool"]["semantic_release"][
                "version_variable"
            ][0]
            self.assertEqual(
                version_variable,
                "pyproject.toml:version",
                f"Unexpected version_variable value: {version_variable}",
            )
            version_file = version_variable.split(":")[0]
            self.assertTrue(
                os.path.exists(version_file),
                f"{version_file} does not exist",
            )


if __name__ == "__main__":
    unittest.main()
