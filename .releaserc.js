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
    { "type": ".*build.*", "release": "patch" },
    { "type": ".*chore.*", "release": "patch" },
    { "type": ".*ci.*", "release": "patch" },
    { "type": ".*docs.*", "release": "patch" },
    { "type": ".*feat.*", "release": "minor" },
    { "type": ".*fix.*", "release": "patch" },
    { "type": ".*perf.*", "release": "patch" },
    { "type": ".*refactor.*", "release": "patch" },
    { "type": ".*revert.*", "release": "patch" },
    { "type": ".*style.*", "release": "patch" },
    { "type": ".*test.*", "release": "patch" },
    { "type": ".*other.*", "release": "patch" }
  ],
  parserOpts: {
    headerPattern: /^(\[[^\]]*\])?\s*(?::\s*([^\s:]+))?\s*(.*)$/,
    noteKeywords: ["BREAKING CHANGE", "BREAKING CHANGES"]
  },
  writerOpts: {
    commitsSort: ["subject", "scope"]
  }
};
