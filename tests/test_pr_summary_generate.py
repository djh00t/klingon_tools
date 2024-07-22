import subprocess
import unittest


class TestPRSummaryGenerate(unittest.TestCase):
    def test_pr_summary_generate(self):
        # Run the pr-summary-generate command
        result = subprocess.run(
            ["pr-summary-generate"], capture_output=True, text=True
        )

        # Check that the command ran without errors
        self.assertEqual(result.returncode, 0)

        # Check that there is some output
        self.assertGreater(len(result.stdout), 0)


if __name__ == "__main__":
    unittest.main()
