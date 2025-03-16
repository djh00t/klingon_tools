"""Tests for Ollama installation and functionality.

This module contains pytest functions for testing Ollama installation,
API connectivity, model availability, and basic model functionality.
"""

import json
import platform
import re
import shutil
import subprocess
from typing import Dict

import pytest
import requests

# Skip entire module if not on macOS
if platform.system() != "Darwin":
    pytest.skip(
        "Ollama tests only supported on macOS",
        allow_module_level=True
    )

# Check if Ollama is installed
OLLAMA_INSTALLED = shutil.which("ollama") is not None

if not OLLAMA_INSTALLED:
    pytest.skip(
        "Ollama is not installed, skipping tests",
        allow_module_level=True
    )

OLLAMA_URL = "http://localhost:11434"


def pytest_addoption(parser):
    """Add command-line option for skipping LLM tests."""
    parser.addoption(
        "--run-ollama",
        action="store_true",
        default=False,
        help="Run tests that require Ollama"
    )


@pytest.fixture(scope="session")
def run_ollama_tests(request):
    """Fixture to access the --run-ollama flag."""
    return request.config.getoption("--run-ollama")


def ollama_cli_version() -> Dict[str, bool | str | None]:
    """Capture and interpret the output of the `ollama --version` command.

    Returns:
        A dictionary with Ollama CLI installation information.

    The dictionary contains the following key-value pairs:
        - ollama_cli_installed (bool): Whether the Ollama CLI is installed.
        - ollama_cli_version (str | None): Ollama CLI version if installed.
        - ollama_server_running (bool): Whether the Ollama server is running.
    """
    result: Dict[str, bool | str | None] = {
        "ollama_cli_installed": False,
        "ollama_cli_version": None,
        "ollama_server_running": True
    }

    try:
        process = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        result["ollama_cli_installed"] = True
        output = process.stdout + process.stderr

        version_match = re.search(r"ollama version is (\d+\.\d+\.\d+)", output)
        if version_match:
            result["ollama_cli_version"] = version_match.group(1)
        else:
            # If the version format changes, try alternative pattern
            alt_version_match = re.search(r"version\s+(\d+\.\d+\.\d+)", output)
            if alt_version_match:
                result["ollama_cli_version"] = alt_version_match.group(1)

    except (subprocess.CalledProcessError, FileNotFoundError):
        result["ollama_cli_installed"] = False
        result["ollama_server_running"] = False

    return result


@pytest.fixture(scope="module")
def ollama_info_fixture():
    """Provide Ollama CLI information for all tests."""
    return ollama_cli_version()


def test_ollama_cli_installed(ollama_info_fixture):
    """Test if the Ollama CLI is installed."""
    assert ollama_info_fixture['ollama_cli_installed'], (
        "Ollama CLI is not installed"
    )
    print(f"ollama_cli_installed: {ollama_info_fixture['ollama_cli_installed']}")


@pytest.mark.depends(on=['test_ollama_cli_installed'])
def test_ollama_cli_version(ollama_info_fixture):
    """Test if the Ollama CLI version is correctly captured."""
    assert ollama_info_fixture['ollama_cli_version'] is not None, (
        "Ollama CLI version not found"
    )
    version = ollama_info_fixture['ollama_cli_version']
    assert re.match(r'\d+\.\d+\.\d+', version), (
        f"Invalid Ollama CLI version format: {version}"
    )
    print(f"ollama_cli_version: {version}")


@pytest.mark.depends(on=['test_ollama_cli_version'])
def test_ollama_server_running(ollama_info_fixture):
    """Test if the Ollama server is running."""
    assert ollama_info_fixture['ollama_server_running'], "Ollama server is not running"
    print(f"ollama_server_running: {ollama_info_fixture['ollama_server_running']}")


@pytest.mark.depends(
    on=['test_ollama_server_running']
)
def test_can_connect_to_ollama():
    """Check if the Ollama API is accessible."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/version", timeout=5)
        response.raise_for_status()
        assert response.status_code == 200, (
            f"Expected status code 200, got {response.status_code}"
        )
        print(f"Successfully connected to Ollama API: {response.json()}")
    except requests.RequestException as e:
        pytest.fail(f"Failed to connect to Ollama API: {e}")


@pytest.mark.depends(on=['test_can_connect_to_ollama'])
def test_models_available(no_llm):
    """Test if there are any models available on the Ollama server."""
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag set")
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        assert response.status_code == 200, (
            f"Cannot retrieve models, status code: {response.status_code}, "
            f"response: {response.text}"
        )

        models = response.json().get("models", [])
        assert len(models) > 0, "No models available. Please pull a model."

        print(f"Found {len(models)} models on the Ollama server:")
        for model in models:
            print(f"- {model['name']}")
    except requests.RequestException as e:
        pytest.skip(f"Cannot retrieve models from Ollama server: {e}")
    except json.JSONDecodeError as e:
        pytest.skip(f"Invalid JSON response: {e}")


@pytest.mark.depends(on=['test_models_available'])
def test_model_functionality(no_llm):
    """Test basic functionality of an Ollama model."""
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag set")

    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        assert response.status_code == 200, (
            f"Cannot retrieve models, status code: {response.status_code}"
        )

        models = response.json().get("models", [])
        assert len(models) > 0, "No models available to test"

        model_to_test = models[0]["name"]
        print(f"Testing model: {model_to_test}")

        prompt = "Solve `2 + 2`. You **MUST** only return a single number."

        generate_response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"prompt": prompt, "model": model_to_test, "stream": False},
            timeout=30
        )
        assert generate_response.status_code == 200, (
            f"Failed to generate response, status code: "
            f"{generate_response.status_code}"
        )

        result = generate_response.json()
        model_response = result.get("response", "").strip()

        # Check if either "4" or "four" appears in the response
        assert any(
            answer in model_response.lower() for answer in ["4", "four"]
        ), (
            "Unexpected response. Expected '4' or 'four', "
            f"got '{model_response}'"
        )

        print(f"Model {model_to_test} successfully answered the question.")

        for field in ['total_duration', 'load_duration', 'prompt_eval_count',
                      'eval_count']:
            assert field in result, f"Response is missing '{field}'"

        print(
            f"Response metadata: Total duration: {result['total_duration']}ns,"
            f" Load duration: {result['load_duration']}ns, "
            f"Prompt eval count: {result['prompt_eval_count']}, "
            f"Eval count: {result['eval_count']}"
        )

    except requests.RequestException as e:
        pytest.skip(f"Failed to communicate with Ollama server: {e}")
    except json.JSONDecodeError as e:
        pytest.skip(f"Invalid JSON response: {e}")
    except AssertionError as e:
        pytest.fail(str(e))


if __name__ == "__main__":
    pytest.main([__file__])
