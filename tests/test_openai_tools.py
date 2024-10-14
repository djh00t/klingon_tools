# tests/test_openai_tools.py
"""Tests for the OpenAITools class and its methods."""

from unittest.mock import patch, MagicMock
import logging
import pytest

from klingon_tools.openai_tools import OpenAITools


@pytest.fixture
def no_llm(request):
    """Fixture to access the --no-llm flag."""
    return request.config.getoption("--no-llm")


@pytest.fixture(scope="module", autouse=True)
def disable_logging():
    """Disable logging for all tests in this module."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def openai_tools(no_llm):
    """Create an instance of OpenAITools."""
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag")
    return OpenAITools(debug=True)


@patch("klingon_tools.openai_tools.get_commit_log")
def test_generate_pull_request_summary(
    mock_get_commit_log,
    openai_tools,
    no_llm
):
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag")
    """Test the generate_pull_request_summary method."""
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag")
    mock_get_commit_log.return_value.stdout = "commit log content"
    openai_tools.generate_content = MagicMock(
        return_value="Generated PR Summary"
    )

    summary = openai_tools.generate_pull_request_summary()

    openai_tools.generate_content.assert_called_once_with(
        "pull_request_summary", "commit log content"
    )
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag")
    assert summary == "Generated PR Summary"


def test_init_with_valid_api_key(openai_tools, no_llm):
    """Test initialization of OpenAITools with a valid API key."""
    assert openai_tools.debug is True
    assert openai_tools.client is not None


@patch("openai.ChatCompletion.create")
def test_generate_pull_request_title(mock_create, openai_tools, no_llm):
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag")
    """Test the generate_pull_request_title method."""
    mock_create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Generated PR title"))]
    )
    diff = "Some diff content"
    title = openai_tools.generate_pull_request_title(diff)

    assert isinstance(title, str)
    assert len(title) <= 72


@pytest.mark.parametrize(
    "message, expected, should_raise",
    [
        (
            "feat(klingon): add new feature",
            "✨ feat(klingon): add new feature",
            False,
        ),
        ("invalid message", None, True),
        ("feat: minimal valid message", None, True),
        (
            "feat(core): minimal valid message",
            "✨ feat(core): minimal valid message",
            False,
        ),
        (
            "fix(bug): fix critical issue",
            "🐛 fix(bug): fix critical issue",
            False,
        ),
    ],
)
def test_format_message(openai_tools, message, expected, should_raise):
    """Test the format_message method with various inputs."""
    if should_raise:
        with pytest.raises(ValueError):
            openai_tools.format_message(message)
    else:
        formatted_message = openai_tools.format_message(message)
        assert formatted_message == expected


@pytest.mark.parametrize(
    "title, expected",
    [
        ("Short title", "Short title"),
        (
            "This is a very long title that exceeds the maximum character "
            "limit maybe, or does it? I don't know, but it's long.",
            "This is a very long title that exceeds the maximum character "
            "limit maybe...",
        ),
        ("Title   with   multiple   spaces", "Title with multiple spaces"),
        ("Title\nwith\nnewlines", "Title with newlines"),
    ],
)
def test_format_pr_title(openai_tools, title, expected):
    """Test the format_pr_title method with various inputs."""
    formatted_title = openai_tools.format_pr_title(title)
    assert formatted_title == expected


@patch("klingon_tools.openai_tools.get_git_user_info")
def test_signoff_message(mock_get_git_user_info, openai_tools):
    """Test the signoff_message method."""
    mock_get_git_user_info.return_value = ("John Doe", "john@example.com")
    message = "Test commit message"
    signed_message = openai_tools.signoff_message(message)
    assert signed_message == (
        "Test commit message\n\nSigned-off-by: John Doe <john@example.com>"
    )


@patch("klingon_tools.openai_tools.git_stage_diff")
@patch.object(OpenAITools, "generate_content")
@patch.object(OpenAITools, "format_message")
@patch.object(OpenAITools, "signoff_message")
def test_generate_commit_message(
    mock_signoff,
    mock_format,
    mock_generate,
    mock_stage_diff,
    openai_tools,
    no_llm
):
    """Test the generate_commit_message method."""
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag")
    mock_generate.return_value = "feat(test): add new feature"
    mock_format.return_value = "✨ feat(test): add new feature"
    mock_signoff.return_value = (
        "✨ feat(test): add new feature\n\n"
        "Signed-off-by: John <john@example.com>"
    )

    result = openai_tools.generate_commit_message(
        "test.py", MagicMock()
    )

    assert result == (
        "✨ feat(test): add new feature\n\n"
        "Signed-off-by: John <john@example.com>"
    )
    mock_stage_diff.assert_called_once()
    mock_generate.assert_called_once()
    mock_format.assert_called_once()
    mock_signoff.assert_called_once()


@patch.object(OpenAITools, "generate_content")
def test_generate_pull_request_body(mock_generate, openai_tools, no_llm):
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag")
    """Test the generate_pull_request_body method."""
    mock_generate.return_value = "Test PR body"
    result = openai_tools.generate_pull_request_body("Test diff")
    assert result == "Test PR body"
    mock_generate.assert_called_once_with("pull_request_body", "Test diff")


@patch.object(OpenAITools, "generate_content")
@patch.object(OpenAITools, "format_message")
@patch("klingon_tools.openai_tools.git_unstage_files")
def test_generate_release_body(
    mock_unstage, mock_format, mock_generate, openai_tools, no_llm
):
    """Test the generate_release_body method."""
    if no_llm:
        pytest.skip("Skipping LLM tests due to --no-llm flag")
    mock_format.return_value = "Formatted test release body"
    mock_generate.return_value = "Test release body"
    mock_repo = MagicMock()
    mock_repo.git.diff.return_value = "file1.py\nfile2.py"

    result = openai_tools.generate_release_body(mock_repo, "Test diff", True)

    assert result == "Formatted test release body"
    mock_generate.assert_called_once_with("release_body", "Test diff")
    mock_unstage.assert_called_once_with(["file1.py", "file2.py"])
    mock_unstage.assert_called_once_with(["file1.py", "file2.py"])
    mock_unstage.assert_called_once_with(["file1.py", "file2.py"])
    mock_format.assert_called_once_with("Test release body")
    mock_unstage.assert_called_once_with(["file1.py", "file2.py"])


if __name__ == "__main__":
    pytest.main(["-v"])
