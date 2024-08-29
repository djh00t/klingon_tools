# tests/test_ollama.py
"""
This module contains pytest functions for testing Ollama installation and
functionality.

It includes tests for checking Ollama installation, API connectivity, model
availability, and basic model functionality.
"""

import pytest
import subprocess
import requests
import json

# URL for the Ollama API
OLLAMA_URL = "http://localhost:11434"


@pytest.fixture
def no_llm(pytestconfig):
    """
    Fixture to access the --no-llm flag.
    """
    return pytestconfig.getoption("--no-llm")


def is_ollama_installed() -> bool:
    """
    Check if Ollama is installed and accessible in the system PATH.

    Returns:
        bool: True if Ollama is installed and accessible, False otherwise.
    """
    try:
        # Run 'ollama --version' command and capture the output
        output = subprocess.run(
            ["ollama", "--version"], check=True, capture_output=True, text=True
        ).stdout
        # Check if the output contains the version info and no warning about
        # connection
        return (
            "ollama version" in output
            and "Warning: could not connect to a running Ollama instance"
            not in output
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Return False if the command fails or Ollama is not found
        return False


def can_connect_to_ollama() -> bool:
    """
    Check if the Ollama API is accessible.

    Returns:
        bool: True if the API is accessible, False otherwise.
    """
    try:
        # Attempt to connect to the Ollama API
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        # Return True if the status code is 200 (OK)
        return response.status_code == 200
    except requests.RequestException:
        # Return False if there's any request exception
        return False


@pytest.mark.optional
def test_ollama_prerequisites():
    """Test if Ollama is installed and the API is accessible.

    This test checks two prerequisites:
    1. Ollama is installed and accessible in the system PATH.
    2. The Ollama API can be connected to.

    Assertions:
        - Asserts that Ollama is installed and accessible in the system PATH.
        - Asserts that the Ollama API is accessible.

    This test checks two prerequisites:
    1. Ollama is installed and accessible in the system PATH.
    2. The Ollama API can be connected to.

    Raises:
        AssertionError: If either of the prerequisites is not met.
    """
    assert is_ollama_installed(), "Ollama is not installed or not in PATH"
    assert can_connect_to_ollama(), "Cannot connect to Ollama server"


@pytest.mark.dependency(depends=["test_ollama_prerequisites"])
@pytest.mark.optional
def test_models_available():
    """Test if there are any models available on the Ollama server.

    This test depends on the successful completion of
    test_ollama_prerequisites.

    Assertions:
        - Asserts that the status code of the response is 200.
        - Asserts that there are models available on the Ollama server.
        - Prints information about the available models.

    Raises:
        pytest.fail: If there's a request exception or JSON decoding error.
    """
    try:
        # Retrieve the list of models from the Ollama API
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        assert (
            response.status_code == 200
        ), (
            "Cannot retrieve models from Ollama server, "
            f"status code: {response.status_code}, "
            f"response: {response.text}"
        )

        # Parse the JSON response and check if there are any models
        models = response.json().get("models", [])
        assert (
            len(models) > 0
        ), "No models available. Please pull a model to use."

        # Print information about the available models
        print(f"Found {len(models)} models on the Ollama server:")
        for model in models:
            print(f"- {model['name']}")
    except requests.RequestException as e:
        pytest.fail(f"Cannot retrieve models from Ollama server: {e}")
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON response: {e}")


@pytest.mark.dependency(depends=["test_models_available"])
@pytest.mark.optional
def test_model_functionality(no_llm):
    """Test the functionality of an available model on the Ollama server.

    This test depends on the successful completion of test_models_available. It
    selects the first available model and tests it with a simple arithmetic
    question.

    Assertions:
        - Asserts that the status code of the response is 200.
        - Asserts that there are models available to test.
        - Asserts that the model's response to the arithmetic question is
          correct.
        - Asserts that the response contains expected metadata fields.

    Raises:
        pytest.fail: If there's a request exception, JSON decoding error, or
        any other assertion error.
    """
    # Skip the test if the --no-llm flag is set
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag")

    try:
        # Retrieve the list of available models
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        assert (
            response.status_code == 200
        ), "Cannot retrieve models from Ollama server, status code: "
        f"{response.status_code}"

        models = response.json().get("models", [])
        assert len(models) > 0, "No models available to test"

        # Select the first available model for testing
        model_to_test = models[0]["name"]
        print(f"Testing model: {model_to_test}")

        # Define a simple arithmetic question for the model
        prompt = (
            "What is 2 + 2? Please respond with just the numerical answer."
        )

        # Generate a response from the selected model
        generate_response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"prompt": prompt, "model": model_to_test, "stream": False},
        )
        assert (
            generate_response.status_code == 200
        ), "Failed to generate response, status code: "
        f"{generate_response.status_code}"

        # Parse the response and extract the model's answer
        result = generate_response.json()
        model_response = result.get("response", "").strip()

        # Check if the model's response is correct
        assert (
            model_response == "4"
        ), "Unexpected response from model. Expected '4', got "
        f"'{model_response}'"

        print(
            f"Model {model_to_test} successfully answered the arithmetic "
            "question."
        )

        # Verify the presence of expected metadata in the response
        assert (
            "total_duration" in result
        ), "Response is missing 'total_duration'"
        assert "load_duration" in result, "Response is missing 'load_duration'"
        assert (
            "prompt_eval_count" in result
        ), "Response is missing 'prompt_eval_count'"
        assert "eval_count" in result, "Response is missing 'eval_count'"

        # Print the response metadata
        print(
            f"Response metadata: Total duration: {result['total_duration']}ns,"
            f" Load duration: {result['load_duration']}ns, "
            f"Prompt eval count: {result['prompt_eval_count']}, "
            f"Eval count: {result['eval_count']}"
        )

    except requests.RequestException as e:
        pytest.fail(f"Failed to communicate with Ollama server: {e}")
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON response: {e}")
    except AssertionError as e:
        pytest.fail(str(e))


if __name__ == "__main__":
    pytest.main([__file__])
