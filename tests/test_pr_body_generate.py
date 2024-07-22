import subprocess
import unittest


class TestPRBodyGenerate(unittest.TestCase):
    def test_pr_body_generate(self):
        # Run the pr-body-generate command
        result = subprocess.run(
            ["pr-body-generate"], capture_output=True, text=True
        )

        # Check that the command ran without errors
        self.assertEqual(result.returncode, 0)

        # Check that there is some output
        self.assertGreater(len(result.stdout), 0)


if __name__ == "__main__":
    unittest.main()
