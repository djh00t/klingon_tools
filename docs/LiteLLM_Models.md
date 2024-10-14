# LiteLLM Models for Git Commit Messages

This document provides a comprehensive list of LiteLLM models that can be used for generating git commit messages. Each model is rated based on its abilities and costs. The table below summarizes the available models, indicating whether they are paid or free, and provides a rating of their performance.

## Model Ratings

| Model Name                | Payment Status | Rating                  | Notes                                                                 |
|---------------------------|----------------|-------------------------|-----------------------------------------------------------------------|
| gpt-4o                    | Paid           | Excellent               | High-quality output, recommended for professional use.                |
| gpt-4o-mini               | Paid           | Very Good               | Smaller version of gpt-4o, still very effective.                      |
| claude-3-haiku-20240307   | Paid           | Very Good               | Reliable and consistent performance.                                  |
| chatgpt-4o-latest         | Paid           | Very Good               | Latest version, performs well.                                        |
| deepseek-coder-v2         | Free           | Very Good               | Excellent for coding-related tasks.                                   |
| codestral-latest          | Paid           | Very Good               | High-quality output, suitable for various tasks.                      |
| groq/llama-3.1-70b-versatile | Freemium     | Excellent               | High-quality output, free up to a point, paid for better access.      |
| groq/mixtral-8x7b-32768   | Freemium       | Very Good               | Reliable and consistent performance, free up to a point.              |
| groq/gemma-7b-it          | Freemium       | Very Good               | Suitable for various tasks, free up to a point.                       |
| mistral-small-latest      | Free           | Good Content            | Produces good content but may have some limitations.                  |
| mistral-nemo              | Free           | Good Content, Formatting Issues | Good content but formatting can be inconsistent.                      |
| phi3:mini                 | Free           | Overly Verbose          | Tends to produce verbose output.                                      |
| llama2:latest             | Free           | Good Content, Extra Content | Good content but includes additional, sometimes unnecessary, content. |
| llama3.1:latest           | Free           | Good Content, Extra Content | Similar to llama2, good content but with extra content.               |
| codeqwen:latest           | Free           | Lacks Conventional Commit Knowledge | Does not understand conventional commit formats well.                 |
| codellama:latest          | Free           | Lacks Breaking Change Understanding | Does not understand what a breaking change is.                        |

## Usage

To use these models, you can initialize the `LiteLLMTools` class with the desired model. Below is an example of how to initialize and use the tools:

```python
from klingon_tools.litellm_tools import LiteLLMTools

# Initialize LiteLLMTools with the desired models
tools = LiteLLMTools(
    debug=True,
    model_primary="gpt-4o-mini",
    model_secondary="claude-3-haiku-20240307"
)

# Generate a commit message
diff = "Your diff content here"
commit_message = tools.generate_content("commit_message_system", diff)
print(commit_message)
```

For more details on the available models and their costs, visit [LiteLLM Models](https://models.litellm.ai/).
