import subprocess
import os
import openai

# Authenticate with OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Collect changelog data
changelog = subprocess.run(
    [
        "git",
        "log",
        '--pretty=format:"%s"',
        "$(git",
        "describe",
        "--tags",
        "--abbrev=0)..HEAD",
    ],
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()

# Generate release notes
response = openai.Completion.create(
    engine="gpt-3.5-turbo",
    prompt=f"Generate release notes from the following changelog: \
        \
    {changelog}",
    max_tokens=500,
)

release_notes = response.choices[0].text.strip()

# Save release notes to CHANGELOG.md
with open("CHANGELOG.md", "a") as f:
    f.write(f"\n## New Release\n\n{release_notes}")

# Draft the release (example with GitHub CLI)
subprocess.run(
    [
        "gh",
        "release",
        "create",
        "draft",
        "--notes",
        release_notes,
        "--target",
        "main",
    ],
    check=True,
)
