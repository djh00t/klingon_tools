module.exports = {
  branches: ["main", "release"],
  repositoryUrl: "https://github.com/djh00t/klingon_tools.git",
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/github",
    "@semantic-release/git",
    [
      "@semantic-release/exec",
      {
        "prepareCmd": "python setup.py sdist bdist_wheel",
        "publishCmd": "twine upload dist/* -u __token__ -p $PYPI_USER_AGENT"
      }
    ],
  ],
};
