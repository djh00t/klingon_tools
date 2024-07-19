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
        "prepareCmd": "python -m build",
        "publishCmd": "twine upload dist/* -u __token__ -p $PYPI_USER_AGENT"
      }
    ],
  ],
  preset: "conventionalcommits",
  releaseRules: [
    { "type": "^(?:.{0,2})build", "release": "patch" },
    { "type": "^(?:.{0,2})chore", "release": "patch" },
    { "type": "^(?:.{0,2})ci", "release": "patch" },
    { "type": "^(?:.{0,2})docs", "release": "patch" },
    { "type": "^(?:.{0,2})feat", "release": "minor" },
    { "type": "^(?:.{0,2})fix", "release": "patch" },
    { "type": "^(?:.{0,2})perf", "release": "patch" },
    { "type": "^(?:.{0,2})refactor", "release": "patch" },
    { "type": "^(?:.{0,2})revert", "release": "patch" },
    { "type": "^(?:.{0,2})style", "release": "patch" },
    { "type": "^(?:.{0,2})test", "release": "patch" },
    { "type": "^(?:.{0,2})other", "release": "patch" }
  ],
  parserOpts: {
    noteKeywords: ["BREAKING CHANGE", "BREAKING CHANGES"]
  },
  writerOpts: {
    commitsSort: ["subject", "scope"]
  }
};
