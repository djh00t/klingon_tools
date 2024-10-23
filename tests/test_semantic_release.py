# tests/test_semantic_release.py
"""
Tests for semantic release configuration.

This module contains pytest-style unit tests for verifying the semantic release
configuration in package.json and pyproject.toml files.
"""

import os
import json
import toml
from typing import Dict, Any
import pytest


def test_package_json_exists() -> None:
    """Test if package.json file exists.

    Assertions:
    1. Check that the package.json file exists in the current directory.
    """
    assert os.path.exists("package.json"), "package.json does not exist"


def test_pyproject_toml_exists() -> None:
    """Test if pyproject.toml file exists.

    Assertions:
    1. Check that the pyproject.toml file exists in the current directory.
    """
    assert os.path.exists("pyproject.toml"), "pyproject.toml does not exist"


import re

def test_package_json_version() -> None:
    """Test if package.json contains a valid version.

    Assertions:
    1. Check that the package.json file contains a "version" key.
    2. Verify that the "version" value is a string.
    3. Ensure that the version string follows semantic versioning format.
    """
    with open("package.json", "r") as f:
        data = json.load(f)

    assert "version" in data, "version key not found in package.json"
    assert isinstance(data["version"], str), "version in package.json is not a string"

    # Semantic Versioning regex pattern
    semver_pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"

    assert re.match(semver_pattern, data["version"]), f"Version '{data['version']}' does not follow semantic versioning format"


def test_pyproject_toml_version() -> None:
    """Test if pyproject.toml contains valid semantic release configuration.

    Assertions:
    1. Check that the pyproject.toml file contains a "tool" section.
    2. Verify that the "tool" section contains a "semantic_release" section.
    3. Ensure that the "semantic_release" section contains a "version_variable"
    key.
    4. Check that the "version_variable" key is a list and is not empty.
    5. Verify that the first item in the "version_variable" list is
    "pyproject.toml:version".
    6. Ensure that the file specified in the "version_variable" exists.
    """
    with open("pyproject.toml", "r") as f:
        data = toml.load(f)

    assert_pyproject_structure(data)
    assert_version_variable(data)


def assert_pyproject_structure(data: Dict[str, Any]) -> None:
    """
    Assert the structure of pyproject.toml.

    Args:
        data: The parsed content of pyproject.toml.

    Raises:
        AssertionError: If the structure is invalid.
    """
    assert "tool" in data, "tool section not found in pyproject.toml"
    assert (
        "semantic_release" in data["tool"]
    ), "semantic_release section not found in pyproject.toml"
    assert (
        "version_variable" in data["tool"]["semantic_release"]
    ), "version_variable key not found in pyproject.toml"


def assert_version_variable(data: Dict[str, Any]) -> None:
    """
    Assert the version_variable in pyproject.toml.

    Args:
        data: The parsed content of pyproject.toml.

    Raises:
        AssertionError: If the version_variable is invalid.
    """
    version_variable = data["tool"]["semantic_release"]["version_variable"]
    assert isinstance(
        version_variable, list), "version_variable should be a list"
    assert len(version_variable) > 0, "version_variable list is empty"

    version_spec = version_variable[0]
    assert (
        version_spec == "pyproject.toml:version"
    ), f"Unexpected version_variable value: {version_spec}"

    version_file = version_spec.split(":")[0]
    assert os.path.exists(version_file), f"{version_file} does not exist"


if __name__ == "__main__":
    pytest.main(["-v"])
