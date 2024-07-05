"""
Setup module for klingon_tools.

This module uses setuptools to package the klingon_tools library.
"""

import os
import re
import sys
from setuptools import find_packages, setup
from setuptools._vendor.packaging.version import InvalidVersion


def get_version():
    """
    Retrieve the version of the package from the version.py file.

    Returns:
        str: The version string.

    Raises:
        RuntimeError: If the version string cannot be found.
    """
    version_file = os.path.join(os.path.dirname(__file__), "version.py")
    with open(version_file, encoding="utf-8") as f:
        code = f.read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", code, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def set_version(version):
    """
    Update the version in the version.py file.

    Args:
        version (str): The new version string.
    """
    version_file = os.path.join(os.path.dirname(__file__), "version.py")
    with open(version_file, "r+") as f:
        content = f.read()
        content_new = re.sub(
            r'__version__ = "[^"]+"', f'__version__ = "{version}"', content
        )
        f.seek(0)
        f.write(content_new)
        f.truncate()


def convert_version(version):
    """
    Convert the semantic-release version to PEP 440 compatible version.

    Args:
        version (str): The version string to convert.

    Returns:
        str: The converted version string.
    """
    match = re.match(r"(\d+\.\d+\.\d+)(?:-(\w+)\.(\d+))?", version)
    if match:
        base_version, prerelease, number = match.groups()
        if prerelease:
            if prerelease == "release":
                prerelease = "rc"
            return f"{base_version}{prerelease}{number}"
        return base_version
    raise InvalidVersion(f"Invalid version: '{version}'")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "set_version":
        if len(sys.argv) != 3:
            print("Usage: python setup.py set_version <new_version>")
            sys.exit(1)
        converted_version = convert_version(sys.argv[2])
        set_version(converted_version)
        print(f"Version set to {converted_version}")
        sys.exit(0)

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="klingon_tools",
    version=get_version(),
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "push=klingon_tools.push:main",
            "gh-actions-update=klingon_tools.gh_actions_update:main",
            "pr-title-generate=klingon_tools.entrypoints:gh_pr_gen_title",
            "pr-summary-generate=klingon_tools.entrypoints:gh_pr_gen_summary",
            "pr-context-generate=klingon_tools.entrypoints:gh_pr_gen_context",
            "pr-body-generate=klingon_tools.entrypoints:gh_pr_gen_body",
        ],
    },
    install_requires=[
        "openai",
        "gitpython",
        "argparse",
        "requests",
        "httpx",
        "pandas",
        "flask",
        "windows-curses; platform_system == 'Windows'",
        "watchdog",
        "pyyaml",
        "pytest",
        "ruamel.yaml",
        "pre-commit",
        "psutil",
    ],
    include_package_data=True,
    description=(
        "A set of utilities for running and logging shell commands in a "
        "user-friendly manner."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="David Hooton",
    author_email="klingon_tools+david@hooton.org",
    url="https://github.com/djh00t/klingon_tools",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
