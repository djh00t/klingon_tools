module.exports = {
  branches: [
    { name: "main" },
    { name: "release", prerelease: true },
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
    [
      "@semantic-release/exec",
      {
        prepareCmd: "gh pr create --title 'chore(release): \\${nextRelease.version}' \
          --body 'This PR includes the release \\${nextRelease.version}.\n\n\\${nextRelease.notes}' \
          --base main --head release",
      },
    ],
  ],
};
