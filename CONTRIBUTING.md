# Contributing to klingon_tools

Thank you for considering contributing to **klingon_tools**! Follow this guide to ensure a smooth contribution process. Please ensure your contributions adhere to the project’s guidelines outlined below.

## Table of Contents

1. [Development Workflow](#development-workflow)
2. [Forking and Local Development](#forking-and-local-development)
3. [Style Guidelines](#style-guidelines)
   - [Git Commit Messages](#git-commit-messages)
   - [Python Style Guide](#python-style-guide)
4. [Tests and Pre-Commit Hooks](#tests-and-pre-commit-hooks)
5. [Pull Request and Review Process](#pull-request-and-review-process)
6. [License](#license)

## Development Workflow

This project follows a structured workflow to ensure all contributions are properly tracked and tested.

1. **Create an Issue**: 
   - If you find a bug or want to suggest a new feature, create a GitHub issue.
   - Describe the problem or feature in detail.

2. **Create a Development Branch**: 
   - Once an issue is created, a development branch is created and linked to the issue by the maintainers.
   - For third-party developers, **fork the repository** and create a local development branch based on the linked issue branch. Your local development branch should be named in the format `feature/issue-<issue-number>` or `bugfix/issue-<issue-number>`.

3. **Make Changes**: 
   - Implement your changes in your development branch.
   - Ensure you update relevant documentation and unit tests to reflect your changes.

4. **Push Changes**: 
   - Push your branch to your fork on GitHub and open a pull request (PR) against the linked development branch.

5. **Run Tests**: 
   - GitHub Actions will automatically run the test suite.
   - A pre-release PR will be generated or updated if it already exists. Pre-release tests will run.

6. **Review Process**: 
   - Once all tests pass and there are no merge conflicts, tag **@djh00t** for a code review.
   - Address any feedback from the review process.

7. **Finalization**: 
   - Once the PR is approved, the pre-release is published on GitHub and Test PyPI.
   - A release PR is generated and, once approved, the release is published on GitHub and PyPI.
   - The associated issue will be closed and linked to the final PR.

## Forking and Local Development

1. **Fork the repository**:
   - Fork the `klingon_tools` repository to your GitHub account.
   - Clone your fork to your local machine.

   ```bash
   git clone https://github.com/YOUR_USERNAME/klingon_tools.git
   cd klingon_tools
   ```

2. **Create a branch linked to the development branch**:
   - Check out the issue-linked development branch, then create your local development branch.

   ```bash
   git checkout -b feature/issue-<issue-number>
   ```

3. **Commit your changes**:
   - Ensure all commits use **Conventional Commits** format.
   - All commits must be signed off using `--signoff`.

   ```bash
   git commit -m "feat(scope): description" --signoff
   ```

4. **Push your branch and open a pull request**:
   - Push your local branch to your fork and create a pull request against the development branch.

   ```bash
   git push origin feature/issue-<issue-number>
   ```

## Style Guidelines

### Git Commit Messages

All commit messages must follow the **Conventional Commits** format. Every commit message must have a type, scope, and description.

Examples:

```
feat(api): add new endpoint for user data

fix(auth): resolve login failure issue with token expiration

docs(readme): update contributing guidelines
```

Types include:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation updates
- `style`: Code formatting (no functionality changes)
- `refactor`: Code restructuring (no functionality changes)
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Sign-off every commit** using `--signoff` to show you agree with the Developer Certificate of Origin (DCO).

### Python Style Guide

- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- Use `pre-commit` hooks configured in `.pre-commit-config.yaml`.

## Tests and Pre-Commit Hooks

We use `pytest` for testing and `pre-commit` hooks to ensure code quality. Before pushing changes, ensure all tests pass and pre-commit hooks are run.

1. Install dependencies using **Poetry**:

   ```bash
   poetry install
   ```

2. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

3. Run tests:

   ```bash
   make test
   ```

4. Run the pre-commit checks manually:

   ```bash
   pre-commit run --all-files
   ```

## Pull Request and Review Process

Once your changes are complete:

1. Ensure all tests pass and the code is free of merge conflicts.
2. Open a pull request (PR) against the issue-linked development branch.
3. Tag **@djh00t** to review the PR.
4. Address feedback as necessary.
5. Once the PR is approved:
   - The pre-release will be published on GitHub and Test PyPI.
   - A release PR will be generated, and once approved, it will be merged and published on PyPI.

## License

By contributing, you agree that your contributions will be licensed under the same license as this project.
