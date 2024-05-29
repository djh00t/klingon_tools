# push/push Script

## Overview

The `push/push` script automates the process of generating commit messages based on staged changes, committing those changes, and handling file changes in a git repository. It utilizes the OpenAI API to generate commit messages following the Conventional Commits standard.

## Features

- **Auto-commit**: Automatically generates commit messages based on staged changes.
- **Pre-commit Hooks**: Runs pre-commit hooks to ensure code quality.
- **Flux Reconciliation**: Reconciles flux sources and kustomizations.
- **Environment Variable Checks**: Ensures required environment variables are set.
- **Error Handling**: Handles errors and retries operations as needed.

## Installation

1. **Clone the Repository**:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install Dependencies**:
    Ensure you have `pre-commit` and `flux` installed. If not, the script will attempt to install them using Homebrew.
    ```sh
    brew install pre-commit flux
    ```

3. **Set Up OpenAI API Key**:
    Export your OpenAI API key as an environment variable:
    ```sh
    export OPENAI_API_KEY=<your-openai-api-key>
    ```

4. **Configuration File**:
    Ensure the `.pushrc` configuration file is present in the root directory of your git repository. If not, the script will copy a template from `scripts/.pushrc_template`.

## Usage

Run the script from the root directory of your git repository:
```sh
./push/push
```

### Optional Arguments

You can specify specific files to handle:
```sh
./push/push <file1> <file2> ...
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key.
- `NO_COMMIT`: Set to `true` to skip committing changes.
- `NO_FLUX`: Set to `true` to skip flux reconciliation.
- `NO_PRE_COMMIT`: Set to `true` to skip running pre-commit hooks.
- `NO_PUSH`: Set to `true` to skip pushing changes to the remote repository.
- `NO_SAVE_API`: Set to `true` to skip saving API responses.

## Example

```sh
export OPENAI_API_KEY=your_openai_api_key
./push/push
```

This will generate commit messages for staged changes, run pre-commit hooks, reconcile flux sources, and push changes to the remote repository.

## License

This script is licensed under the MIT License. See the LICENSE file for more details.
