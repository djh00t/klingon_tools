import pytest
import subprocess
import requests
import os


# Example: This test checks if the 'ollama' dependency is installed
@pytest.mark.optional  # Mark as optional
def is_ollama_installed():
    """Check if Ollama is installed by running 'ollama --version'."""
    try:
        output = subprocess.run(
            ["ollama", "--version"], check=True, capture_output=True, text=True
        ).stdout
        if "Warning: could not connect to a running Ollama instance" in output:
            return False
        elif "ollama version is" in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


@pytest.mark.dependency(
    depends=["is_ollama_installed"]
)  # This test depends on 'can_connect_to_ollama' to pass
@pytest.mark.optional  # Mark as optional
def can_connect_to_ollama():
    """Check if we can connect to Ollama server."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except requests.RequestException:
        return False


@pytest.mark.dependency(
    depends=["can_connect_to_ollama"]
)  # This test depends on 'can_connect_to_ollama' to pass
@pytest.mark.optional  # Mark as optional
@pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") is not None,
    reason="Skipping tests in GitHub Actions environment",
)  # Skip if running in GitHub Actions environment
def test_ollama_installed():
    """Test if Ollama is installed."""
    assert is_ollama_installed(), "Ollama is not installed or not in PATH"


# This test depends on 'can_connect_to_ollama' to pass
@pytest.mark.dependency(depends=["can_connect_to_ollama"])
@pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") is not None,
    reason="Skipping tests in GitHub Actions environment",
)
def test_ollama_connection():
    """Test if we can connect to Ollama server."""
    assert can_connect_to_ollama(), "Cannot connect to Ollama server"


if __name__ == "__main__":
    pytest.main([__file__])
