import os

import openai

# Authenticate with OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Get the list of changed files and the diff
changed_files = os.popen("git diff --name-only HEAD^").read().splitlines()
diff = os.popen("git diff HEAD^").read()

# Generate AI-based review comments
response = openai.Completion.create(
    engine="davinci-codex",
    prompt=f"Review the following code changes:\n\n{diff}\n\nProvide review comments:",
    max_tokens=500,
)

comments = response.choices[0].text.strip()

# Output comments to the console or post them to the PR
print(comments)
