import os
import unittest
import argparse
from klingon_tools.gh_actions_update import find_github_actions


class TestGHActionsUpdate(unittest.TestCase):
    def test_find_github_actions(self):
        # Get the actual YAML files in .github/workflows/
        workflow_files = []
        for root, _, files in os.walk(".github/workflows/"):
            for file in files:
                if file.endswith(".yml") or file.endswith(".yaml"):
                    workflow_files.append(os.path.join(root, file))

        # Create a Namespace object for the arguments
        args = argparse.Namespace(
            file=None,
            owner=None,
            repo=None,
            job=None,
            action=None,
            no_emojis=False,
            quiet=True,
        )

        # Call the function
        actions = find_github_actions(args)

        # Check if the returned actions contain the actual YAML files
        for workflow_file in workflow_files:
            self.assertTrue(any(workflow_file in key for key in actions))


if __name__ == "__main__":
    unittest.main()
