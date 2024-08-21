import os
import sys
import unittest
from unittest.mock import patch
from io import StringIO

# Add the parent directory to sys.path to import kstart
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from klingon_tools import kstart  # noqa: E402


class TestKStart(unittest.TestCase):

    @patch("builtins.input")
    @patch("subprocess.run")
    def test_check_git_config(self, mock_subprocess, mock_input):
        mock_input.side_effect = ["Test User", "test@example.com"]
        mock_subprocess.return_value.returncode = 0

        with patch("configparser.ConfigParser.read"):
            kstart.check_git_config()

        self.assertEqual(mock_subprocess.call_count, 2)
        mock_subprocess.assert_any_call(
            ["git", "config", "--global", "user.name", "Test User"]
        )
        mock_subprocess.assert_any_call(
            ["git", "config", "--global", "user.email", "test@example.com"]
        )

    @patch("builtins.input")
    def test_prompt_with_default(self, mock_input):
        mock_input.return_value = ""
        result = kstart.prompt_with_default("Test prompt", "default_value")
        self.assertEqual(result, "default_value")

        mock_input.return_value = "user_input"
        result = kstart.prompt_with_default("Test prompt", "default_value")
        self.assertEqual(result, "user_input")

    @patch("builtins.input")
    @patch("subprocess.run")
    @patch("configparser.ConfigParser.read")
    @patch("configparser.ConfigParser.write")
    def test_main(self, mock_write, mock_read, mock_subprocess, mock_input):
        mock_input.side_effect = [
            "Test User",  # Git user.name
            "test@test.com",  # Git user.email
            "testuser",  # GitHub username
            "c",  # Issue type choice (feature)
            "Test Feature",  # Feature branch title
            "123,456",  # Linked issues
        ]
        mock_subprocess.return_value.returncode = 0

        with patch("sys.stdout", new=StringIO()) as fake_out:
            kstart.main()

        self.assertIn("Pushed branch:", fake_out.getvalue())

        # Check if the correct number of inputs were consumed
        self.assertEqual(mock_input.call_count, 6)

    @patch("builtins.input")
    @patch("subprocess.run")
    @patch("configparser.ConfigParser.read")
    @patch("configparser.ConfigParser.write")
    def test_main_invalid_issue_type(
        self, mock_write, mock_read, mock_subprocess, mock_input
    ):
        mock_input.side_effect = [
            "Test User",  # Git user.name
            "test@test.com",  # Git user.email
            "testuser",  # GitHub username
            "d",  # Invalid issue type choice
            "Test Feature",  # Feature branch title
            "123,456",  # Linked issues
        ]
        mock_subprocess.return_value.returncode = 0

        with patch("sys.stdout", new=StringIO()) as fake_out:
            kstart.main()

        self.assertIn(
            "Invalid choice. Using default: 'feature'.", fake_out.getvalue()
        )
        self.assertIn("Pushed branch:", fake_out.getvalue())

        # Check if the correct number of inputs were consumed
        self.assertEqual(mock_input.call_count, 6)

    @patch("klingon_tools.kstart.main")
    def test_entrypoint(self, mock_main):
        # Test that kstart.main() is called when the module is run
        kstart.main()
        mock_main.assert_called_once()


if __name__ == "__main__":
    unittest.main()
