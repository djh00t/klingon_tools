module.exports = {
  branches: ["main"],
  repositoryUrl: "https://github.com/djh00t/klingon_tools.git",
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    [
      "@semantic-release/exec",
      {
        prepareCmd: "python setup.py set_version ${nextRelease.version} && python setup.py sdist bdist_wheel",
      },
    ],
    [
      "@semantic-release/git",
      {
        assets: ["CHANGELOG.md", "setup.py", "version.py"],
        message:
          "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
      },
    ],
    [
      "@semantic-release/github",
      {
        assets: "dist/*",
      },
    ],
    [
      "@semantic-release/exec",
      {
        publishCmd: "twine upload dist/* -u __token__ -p $PYPI_TOKEN",
      },
    ],
    [
      "@semantic-release/exec",
      {
        prepareCmd: `gh pr create --title 'chore(release): \${nextRelease.version}' \
          --body 'This PR includes the release \${nextRelease.version}.\n\n\${nextRelease.notes}' \
          --base main --head release`,
      },
    ],
  ],
  preset: "angular",
  release: {
    branches: ["main"],
    tagFormat: "${version}",
    verifyConditions: ["@semantic-release/github"],
    analyzeCommits: {
      preset: "angular",
      releaseRules: [
        { type: "fix", release: "patch" },
        { type: "feat", release: "minor" },
        { type: "BREAKING CHANGE", release: "major" },
        { type: "chore", release: false },
        { type: "docs", release: false },
        { type: "style", release: false },
        { type: "refactor", release: false },
        { type: "perf", release: false },
        { type: "test", release: false },
      ],
    },
    generateNotes: {
      preset: "angular",
    },
  },
};
