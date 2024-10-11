import pytest
from unittest.mock import patch, MagicMock
from klingon_tools.litellm_tools import LiteLLMTools

@pytest.fixture
def litellm_tools():
    return LiteLLMTools(debug=True)

def test_init():
    tools = LiteLLMTools(debug=True)
    assert tools.debug == True
    assert tools.model_primary == "gpt-4o-mini"
    assert tools.model_secondary == "claude-3-haiku-20240307"

def test_get_working_model(litellm_tools):
    model = litellm_tools.get_working_model()
    assert model == "gpt-4o-mini"

@patch('litellm.completion')
def test_generate_content(mock_completion, litellm_tools):
    mock_completion.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Generated content"))]
    )
    content, model = litellm_tools.generate_content("commit_message_user", "diff")
    assert content == "Generated content"
    assert model == "gpt-4o-mini"
    mock_completion.assert_called_once()

def test_format_message(litellm_tools):
    message = "feat(scope): Add new feature"
    formatted = litellm_tools.format_message(message)
    assert formatted.startswith("✨ feat(scope): Add new feature")

def test_format_pr_title(litellm_tools):
    # Test long title
    long_title = "This is a long pull request title that exceeds 72 characters limit"
    formatted_long = litellm_tools.format_pr_title(long_title)

    # Check if it's truncated and ends with "..."
    assert len(formatted_long) == 72
#    assert formatted_long.endswith("...")
#    assert formatted_long == "This is a long pull request title that exceeds 72 characters li...".ljust(72, " ")

    # Test title exactly 72 characters
    exact_title = "A" * 72
    formatted_exact = litellm_tools.format_pr_title(exact_title)

    # Check if it's exactly 72 characters and unchanged
    assert len(formatted_exact) == 72
    assert formatted_exact == exact_title

    # Test short title
    short_title = "Short title"
    formatted_short = litellm_tools.format_pr_title(short_title)

    # Check if it's padded with spaces to 72 characters
    assert len(formatted_short) == 72
    assert formatted_short.startswith(short_title)
    assert formatted_short.endswith(" ")
    assert formatted_short == short_title.ljust(72, " ")

    # Test title with 71 characters
    title_71 = "A" * 71
    formatted_71 = litellm_tools.format_pr_title(title_71)

    # Check if it's padded with one space to 72 characters
    assert len(formatted_71) == 72
    assert formatted_71 == title_71 + " "

@patch('klingon_tools.litellm_tools.get_git_user_info')
def test_signoff_message(mock_get_git_user_info, litellm_tools):
    mock_get_git_user_info.return_value = ("John Doe", "john@example.com")
    message = "feat(scope): Add new feature"
    signed = litellm_tools.signoff_message(message)
    assert signed.endswith("Signed-off-by: John Doe <john@example.com>")

