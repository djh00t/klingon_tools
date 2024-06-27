#!/usr/bin/env python3
import os
from jinja2 import Template
import re
import subprocess

template_path = ".github/workflows/pr_body_template.j2"
with open(template_path) as file_:
    template = Template(file_.read())

os.system("git fetch origin main")
commit_messages = (
    os.popen('git log origin/main..HEAD --pretty=format:"%s"').read().split("\n")
)

types = {
    "build": [],
    "chore": [],
    "ci": [],
    "docs": [],
    "feat": [],
    "fix": [],
    "other": [],
    "perf": [],
    "refactor": [],
    "revert": [],
    "style": [],
    "test": [],
}

emoji_pattern = re.compile(
    "["
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\u2702-\u27B0"  # Dingbats
    "\u24C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)


def remove_emojis_and_leading_spaces(text):
    text = emoji_pattern.sub("", text).strip()
    if len(text) > 1 and text[1] == " ":
        text = text[2:]
    return text


for message in commit_messages:
    message = remove_emojis_and_leading_spaces(message)
    matched = False
    for change_type in types.keys():
        if re.match(
            rf"^[\U0001F300-\U0001F5FF\u2000-\u3300]*{change_type}\(\S+\):",
            message,
            re.UNICODE,
        ) or re.match(
            rf"^[\U0001F300-\U0001F5FF\u2000-\u3300]*{change_type}:",
            message,
            re.UNICODE,
        ):
            types[change_type].append(message)
            matched = True
            break
    if not matched:
        # Remove the first and second character if the second char is a space and try matching again
        if len(message) > 1 and message[1] == " ":
            message = message[2:]
            for change_type in types.keys():
                if re.match(
                    rf"^[\U0001F300-\U0001F5FF\u2000-\u3300]*{change_type}\(\S+\):",
                    message,
                    re.UNICODE,
                ) or re.match(
                    rf"^[\U0001F300-\U0001F5FF\u2000-\u3300]*{change_type}:",
                    message,
                    re.UNICODE,
                ):
                    types[change_type].append(message)
                    matched = True
                    break
    if not matched:
        types["other"].append(message)


def generate_summary():
    result = subprocess.run(["pr-summary-generate"], capture_output=True, text=True)
    return result.stdout.strip()


def generate_motivation_context():
    result = subprocess.run(["pr-context-generate"], capture_output=True, text=True)
    return result.stdout.strip()


def get_branch_name():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_pr_number():
    result = subprocess.run(
        ["gh", "pr", "view", "--json", "number", "--jq", ".number"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


branch_name = get_branch_name()
summary = generate_summary()
motivation_context = generate_motivation_context()
pr_number = get_pr_number()

pr_body = template.render(
    summary=summary,
    branch_name=branch_name,
    actor=os.getenv("GITHUB_ACTOR"),
    pr_number=pr_number,
    motivation_context=motivation_context,
    types=types,
)

print(pr_body)
