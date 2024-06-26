from setuptools import setup, find_packages

import os
import re
from setuptools import setup, find_packages


def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "version.py")
    with open(version_file) as f:
        code = f.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", code, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


setup(
    name="klingon_tools",
    version=get_version(),
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "push=klingon_tools.push:main",
            "gh-actions-update=klingon_tools.gh_actions_update:main",
            "pr-title-generate=klingon_tools.entrypoints:gh_pr_gen_title",
            "pr-body-generate=klingon_tools.entrypoints:gh_pr_gen_body",
        ],
    },
    install_requires=[
        "openai",
        "argparse",
        "requests",
        "httpx",
        "pandas",
        "flask",
        "windows-curses; platform_system == 'Windows'",
        "watchdog",
        "pyyaml",
        "pytest",
    ],
    include_package_data=True,
    description="A set of utilities for running and logging shell commands in a user-friendly manner.",
    long_description=open("README.md").read(),
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
