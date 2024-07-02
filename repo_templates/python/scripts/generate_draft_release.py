import os

import openai

# Authenticate with OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Collect changelog data
changelog = os.popen(
    'git log --pretty=format:"%s" $(git describe --tags --abbrev=0)..HEAD'
).read()

# Generate release notes
response = openai.Completion.create(
    engine="davinci-codex",
    prompt=f"Generate release notes from the following changelog:\n\n{changelog}",
    max_tokens=500,
)

release_notes = response.choices[0].text.strip()

# Save release notes to CHANGELOG.md
with open("CHANGELOG.md", "a") as f:
    f.write(f"\n## New Release\n\n{release_notes}")

# Draft the release (example with GitHub CLI)
os.system(f'gh release create draft --notes "{release_notes}" --target main')
