import pytest
from klingon_tools.git_commit_fix import fix_commit_message


@pytest.mark.parametrize("input_message, expected_output",
                         [("Short message",
                           "Short message"),
                          ("This is a longer message that exceeds the 72 character limit and should be wrapped",  # noqa: E501
                           "This is a longer message that exceeds the 72 character limit and should\nbe wrapped"),  # noqa: E501
                             ("Line 1\nLine 2\nThis is a very long line that exceeds the 72 character limit and should be wrapped\nLine 4",  # noqa: E501
                              "Line 1\nLine 2\nThis is a very long line that exceeds the 72 character limit and should\nbe wrapped\nLine 4"),  # noqa: E501
                             ("A" * 150,
                              "A" * 72 + "\n" + "A" * 72 + "\n" + "A" * 6),
                             ("",
                              ""),
                          ])
def test_fix_commit_message(input_message, expected_output):
    assert fix_commit_message(input_message) == expected_output


def test_fix_commit_message_preserves_newlines():
    input_message = "Line 1\n\nLine 3\nLine 4"
    expected_output = "Line 1\n\nLine 3\nLine 4"
    assert fix_commit_message(input_message) == expected_output


def test_fix_commit_message_handles_long_words():
    input_message = "This_is_a_very_long_word_that_exceeds_the_72_character_limit_and_should_be_split"  # noqa: E501
    expected_output = "This_is_a_very_long_word_that_exceeds_the_72_character_limit_and_should_\nbe_split"  # noqa: E501
    assert fix_commit_message(input_message) == expected_output
