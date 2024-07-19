import pytest
from klingon_tools.openai_tools import OpenAITools


def test_init_with_valid_api_key():
    openai_tools = OpenAITools(debug=True)
    assert openai_tools.debug
    assert openai_tools.client is not None


def test_generate_content(mocker):
    mock_response = mocker.Mock()
    mock_response.choices = [
        mocker.Mock(message=mocker.Mock(content="Generated content"))
    ]
    mocker.patch("openai.ChatCompletion.create", return_value=mock_response)
    openai_tools = OpenAITools()
    template_key = "commit_message_user"
    diff = "Some diff content"
    content = openai_tools.generate_content(template_key, diff)
    assert content == "Generated content"


def test_generate_pull_request_title(mocker):
    mocker.patch(
        "openai.ChatCompletion.create",
        return_value=mocker.Mock(
            choices=[
                mocker.Mock(message=mocker.Mock(content="Generated PR title"))
            ]
        ),
    )
    openai_tools = OpenAITools()
    diff = "Some diff content"
    title = openai_tools.generate_pull_request_title(diff)
    assert isinstance(title, str)
    assert len(title) <= 72


def test_format_message_with_valid_input():
    openai_tools = OpenAITools()
    message = "feat(klingon): add new feature"
    formatted_message = openai_tools.format_message(message)
    assert formatted_message == "✨ feat(klingon): add new feature"


def test_format_message_with_invalid_input():
    openai_tools = OpenAITools()
    message = "invalid message"
    with pytest.raises(ValueError):
        openai_tools.format_message(message)


def test_format_pr_title_with_short_title():
    openai_tools = OpenAITools()
    title = "Short title"
    formatted_title = openai_tools.format_pr_title(title)
    assert formatted_title == "Short title"


def test_format_pr_title_with_long_title():
    openai_tools = OpenAITools()
    title = (
        "This is a very long title that exceeds the maximum character limit "
        "maybe, or does it? I don't know, but it's long."
    )
    formatted_title = openai_tools.format_pr_title(title)
    assert (
        formatted_title
        == "This is a very long title that exceeds the maximum character "
        "limit maybe..."
    )


def test_format_pr_title_with_multiple_spaces():
    openai_tools = OpenAITools()
    title = "Title   with   multiple   spaces"
    formatted_title = openai_tools.format_pr_title(title)
    assert formatted_title == "Title with multiple spaces"


def test_format_pr_title_with_newlines():
    openai_tools = OpenAITools()
    title = "Title\nwith\nnewlines"
    formatted_title = openai_tools.format_pr_title(title)
    assert formatted_title == "Title with newlines"
