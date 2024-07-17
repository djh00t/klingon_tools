module.exports = {
  branches: [
    { name: "release", channel: "release" },
    { name: "main" },
  ],
  repositoryUrl: "https://github.com/djh00t/klingon_tools.git",
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/github",
    "@semantic-release/npm",
    "@semantic-release/git",
    {
      assets: ["CHANGELOG.md", "setup.py", "version.py"],
      message: "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
    }
  ]
],
};
