# openai_tools

The `openai_tools` module provides tools for generating commit messages, pull request titles, and release bodies using OpenAI's API.

## Features

- **Automated Content Generation**: Generate commit messages, pull request titles, and release bodies based on the changes made using the OpenAI API.
- **Message Formatting**: Format messages with line wrapping and sign-off.
- **Unstage Files**: Unstage all staged files.

## Installation

To install the `openai_tools` module, you can use pip:

```sh
pip install klingon_tools
```

## Usage

To use the `openai_tools` module, import it in your script:

```python
from klingon_tools.openai_tools import OpenAITools

# Initialize the OpenAITools class
openai_tools = OpenAITools()

# Generate a commit message
diff = "your_diff_here"
commit_message = openai_tools.generate_commit_message(diff)

# Generate a pull request title
pr_title = openai_tools.generate_pull_request_title(diff)

# Generate a release body
release_body = openai_tools.generate_release_body(diff)
```

### Example Usage

Generate a commit message:

```python
diff = "your_diff_here"
commit_message = openai_tools.generate_commit_message(diff)
print(commit_message)
```

**Expected Output:**

```plaintext
✨ feat(scope): Your commit message

Signed-off-by: Your Name <your.email@example.com>
```

Generate a pull request title:

```python
diff = "your_diff_here"
pr_title = openai_tools.generate_pull_request_title(diff)
print(pr_title)
```

**Expected Output:**

```plaintext
Your pull request title
```

Generate a release body:

```python
diff = "your_diff_here"
release_body = openai_tools.generate_release_body(diff)
print(release_body)
```

**Expected Output:**

```plaintext
Your release body
```

### Environmental Requirements

The `openai_tools` module requires an OpenAI API key to generate content. Set the `OPENAI_API_KEY` environment variable with your OpenAI API key:

```sh
export OPENAI_API_KEY=your_openai_api_key
```

## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
