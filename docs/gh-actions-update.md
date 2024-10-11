# gh-actions-update

The `gh-actions-update` command provides functionality to check and update GitHub Actions versions in YAML workflow files within a repository. It supports filtering by action, job, repository, and owner, and can output results in JSON format or update the workflow files directly.

## Features

- **Check GitHub Actions Versions**: Identify outdated GitHub Actions in your workflow files.
- **Update GitHub Actions Versions**: Automatically update GitHub Actions to their latest versions.
- **Filtering**: Filter actions by owner, repository, job, and action name.
- **JSON Output**: Output the results in JSON format for further processing.

## Installation

To install the `gh-actions-update` tool, you can use pip:

```sh
pip install klingon_tools
```

## Usage

To use the `gh-actions-update` command, run it from the root of your repository:

```sh
gh-actions-update [OPTIONS]
```

### Command-Line Arguments

The following command-line arguments are supported:

- `--action <action>`: Update all instances of a specific action.
- `--debug`: Enable debug logging.
- `--file <file>`: Update actions in a specific file (bash wildcards accepted).
- `--job <job>`: Filter actions by job name.
- `--repo <repo>`: Filter actions by repository name.
- `--owner <owner>`: Filter actions by owner name.
- `--no-emojis`: Disable emojis in output.
- `--quiet`: Suppress startup log messages.
- `--update`: Update outdated actions to the latest version.
- `--json`: Output the results as a JSON object.
- `-h`, `--help`: Show help message and exit.

### Example Usage

Check for outdated GitHub Actions in all workflow files:

```sh
gh-actions-update
```

**Expected Output:**

```plaintext
File                          Owner    Repo     Action Name         Job       Current Latest Status
----------------------------- -------- -------- ------------------- --------- ------- ------- ------
.github/workflows/main.yml    actions  checkout actions/checkout@v2 build     v2      v3      ⬆️
.github/workflows/deploy.yml  actions  setup    actions/setup@v1    deploy    v1      v2      ⬆️
```

Update all outdated GitHub Actions to their latest versions:

```sh
gh-actions-update --update
```

**Expected Output:**

```plaintext
Updating action: actions/checkout from version v2 to v3 in file .github/workflows/main.yml
Updating action: actions/setup from version v1 to v2 in file .github/workflows/deploy.yml
```

Filter actions by a specific owner and repository:

```sh
gh-actions-update --owner actions --repo checkout
```

**Expected Output:**

```plaintext
File                          Owner    Repo     Action Name         Job       Current Latest Status
----------------------------- -------- -------- ------------------- --------- ------- ------- ------
.github/workflows/main.yml    actions  checkout actions/checkout@v2 build     v2      v3      ⬆️
```

Output the results in JSON format:

```sh
gh-actions-update --json
```

**Expected Output:**

```json
{
    ".github/workflows/main.yml:actions:checkout:actions/checkout@v2:build:v2": {
        "file_name": ".github/workflows/main.yml",
        "action_owner": "actions",
        "action_repo": "checkout",
        "action_version_current": "v2",
        "action_name": "actions/checkout@v2",
        "action_name_clean": "actions/checkout",
        "job_name": "build",
        "action_latest_version": "v3"
    },
    ".github/workflows/deploy.yml:actions:setup:actions/setup@v1:deploy:v1": {
        "file_name": ".github/workflows/deploy.yml",
        "action_owner": "actions",
        "action_repo": "setup",
        "action_version_current": "v1",
        "action_name": "actions/setup@v1",
        "action_name_clean": "actions/setup",
        "job_name": "deploy",
        "action_latest_version": "v2"
    }
}
```

### Environmental Requirements

The `gh-actions-update` command requires a GitHub token to authenticate API requests. Set the `GITHUB_TOKEN` environment variable with your GitHub token:

```sh
export GITHUB_TOKEN=your_github_token
```

## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
