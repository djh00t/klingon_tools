import unittest
from unittest.mock import patch, MagicMock
from git import Repo
from klingon_tools.openai_tools import OpenAITools
import logging


class TestOpenAITools(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Suppress logging output during tests
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        # Re-enable logging after tests
        logging.disable(logging.NOTSET)

    @patch("klingon_tools.openai_tools.get_commit_log")
    def test_generate_pull_request_summary(self, mock_get_commit_log):
        # Mock the return value of get_commit_log
        mock_get_commit_log.return_value.stdout = "commit log content"

        # Create an instance of OpenAITools
        openai_tools = OpenAITools()

        # Mock the generate_content method
        openai_tools.generate_content = MagicMock(
            return_value="Generated PR Summary"
        )

        # Call the method to test
        summary = openai_tools.generate_pull_request_summary(
            Repo(), "diff content"
        )

        # Assertions
        openai_tools.generate_content.assert_called_once_with(
            "pull_request_summary", "commit log content"
        )
        self.assertEqual(summary, "Generated PR Summary")

    def test_init_with_valid_api_key(self):
        openai_tools = OpenAITools(debug=True)
        self.assertTrue(openai_tools.debug)
        self.assertIsNotNone(openai_tools.client)

    @patch("openai.ChatCompletion.create")
    def test_generate_pull_request_title(self, mock_create):
        mock_create.return_value = MagicMock(
            choices=[
                MagicMock(message=MagicMock(content="Generated PR title"))
            ]
        )
        openai_tools = OpenAITools()
        diff = "Some diff content"
        title = openai_tools.generate_pull_request_title(diff)
        self.assertIsInstance(title, str)
        self.assertLessEqual(len(title), 72)

    def test_format_message_with_valid_input(self):
        openai_tools = OpenAITools()
        message = "feat(klingon): add new feature"
        formatted_message = openai_tools.format_message(message)
        self.assertEqual(
            formatted_message, "✨ feat(klingon): add new feature"
        )

    def test_format_message_with_invalid_input(self):
        openai_tools = OpenAITools()
        message = "invalid message"
        with self.assertRaises(ValueError):
            openai_tools.format_message(message)

    def test_format_pr_title_with_short_title(self):
        openai_tools = OpenAITools()
        title = "Short title"
        formatted_title = openai_tools.format_pr_title(title)
        self.assertEqual(formatted_title, "Short title")

    def test_format_pr_title_with_long_title(self):
        openai_tools = OpenAITools()
        title = (
            "This is a very long title that exceeds the maximum character "
            "limit maybe, or does it? I don't know, but it's long."
        )
        formatted_title = openai_tools.format_pr_title(title)
        self.assertEqual(
            formatted_title,
            "This is a very long title that exceeds the maximum character "
            "limit maybe...",
        )

    def test_format_pr_title_with_multiple_spaces(self):
        openai_tools = OpenAITools()
        title = "Title   with   multiple   spaces"
        formatted_title = openai_tools.format_pr_title(title)
        self.assertEqual(formatted_title, "Title with multiple spaces")

    def test_format_pr_title_with_newlines(self):
        openai_tools = OpenAITools()
        title = "Title\nwith\nnewlines"
        formatted_title = openai_tools.format_pr_title(title)
        self.assertEqual(formatted_title, "Title with newlines")


if __name__ == "__main__":
    unittest.main()
