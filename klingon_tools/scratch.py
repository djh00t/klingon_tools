from klingon_tools.openai_tools import OpenAITools
import subprocess

# Initialize the OpenAITools class
openai_tools = OpenAITools()


# Get a log of all changes that this PR is ahead of main by.
def get_commits_ahead_of_remote_main():
    # Run the git command to get commits that the current branch is ahead of origin/main
    result = subprocess.run(
        ["git", "--no-pager", "log", "origin/main..HEAD", "--pretty=format:%s"],
        capture_output=True,
        text=True,
        check=True,
    )

    # Split the result by lines to get individual commit messages
    commits = result.stdout.splitlines()
    return commits


if __name__ == "__main__":
    # Get the commits ahead of main
    commits_ahead = get_commits_ahead_of_remote_main()

    #    print(f"Commits ahead of main: {commits_ahead}")

    # Save the commits to a single variable
    commits = ""
    for commit in commits_ahead:
        commits += commit + "\n"

    # Generate a pull request title
    pr_title = openai_tools.generate_pull_request_title(commits)

    # Print the PR title
    print(pr_title)

# Developer Tools
push

# Github AI Tools
gh - pr - gen - title
gh - commit - gen - msg
