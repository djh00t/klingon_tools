from setuptools import setup, find_packages

setup(
    name="klingon_tools",
    version="0.0.7",
    packages=find_packages(),
    install_requires=[
        # No external dependencies required
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
    python_requires='>=3.6',
)
