import subprocess
import unittest


class TestPRTitleGenerate(unittest.TestCase):
    def test_pr_title_generate(self):
        # Run the pr-title-generate command
        result = subprocess.run(
            ["pr-title-generate"], capture_output=True, text=True
        )

        # Split the output into lines
        output_lines = result.stdout.splitlines()

        # Check that there is a line of text output
        self.assertGreater(len(output_lines), 0)

        # Check that its length is 72 characters or less
        self.assertLessEqual(len(output_lines[0]), 72)


if __name__ == "__main__":
    unittest.main()
