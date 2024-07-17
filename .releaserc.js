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
        message: "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
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
  ],
};
