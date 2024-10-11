from klingon_tools.openai_tools import OpenAITools
from klingon_tools.litellm_tools import LiteLLMTools
import logging

# Configure logging to include process name
logging.basicConfig(
    format="%(processName)s - %(levelname)s - %(message)s", level=logging.INFO
)


# Suppress logging from urllib3
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("http.client").setLevel(logging.WARNING)
# logging.getLogger("LiteLLM").setLevel(logging.WARNING)


def compare_generate_content(diff: str):
    openai_tools = OpenAITools(debug=True)
    litellm_tools = LiteLLMTools(
        debug=True,
        model_primary="mistral/codestral-latest",
        # model_primary="ollama_chat/codegemma:2b",
        # model_secondary="ollama_chat/deepseek-coder-v2:latest"
    )

    openai_content = openai_tools.generate_content("commit_message_user", diff)
    litellm_content = litellm_tools.generate_content(
        "commit_message_user", diff
    )

    print("OpenAI Content:")
    print(openai_content)
    print("\nLiteLLM Content:")
    print(litellm_content)

    if openai_content == litellm_content:
        print("\nThe content matches!")
    else:
        print("\nThe content does not match.")


# Example diff to test
diff = "diff --git a/file.txt b/file.txt\nindex 83db48f..bf269f4 100644\n--- a/file.txt\n+++ b/file.txt\n@@ -1 +1 @@\n-Hello World\n+Hello OpenAI"  # noqa
compare_generate_content(diff)
