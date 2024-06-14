import os
import subprocess
import requests


def generate_commit_message(staged_diffs):
    """
    Generates a commit message using the OpenAI API.

    Args:
        staged_diffs (str): The staged changes in the repository.

    Returns:
        str: The generated commit message.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    prompt = f'Generate a git commit message based on these diffs:\n"{staged_diffs}"'
    response = requests.post(
        "https://api.openai.com/v1/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "text-davinci-003",
            "prompt": prompt,
            "temperature": 0.5,
            "max_tokens": 100,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        },
    )
    response.raise_for_status()
    return response.json()["choices"][0]["text"].strip()


def handle_changed_files():
    """
    Handles changed files by generating a commit message for staged changes and committing them.
    """
    staged_diffs = subprocess.check_output(
        ["git", "diff", "--cached", "--name-status"]
    ).decode("utf-8")
    if staged_diffs:
        commit_message = generate_commit_message(staged_diffs)
        subprocess.run(["git", "commit", "-m", commit_message])
        print("Changes committed successfully.")
    else:
        print("No changes to commit.")


def check_environment_variables():
    """
    Checks if required environment variables are set.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")


def main():
    """
    The main function that orchestrates the script's flow.
    """
    try:
        check_environment_variables()
        handle_changed_files()
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
