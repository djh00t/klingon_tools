# klingon_tools

The `klingon_tools` Python library provides a collection of python development
tools and utilities that help automate tasks, handle errors, and simplify the
process of rapid iterative development.

## Table of Contents

| Tool | Description | Link |
| --- | --- | --- |
| gh-actions-update | A utility that reports on and updates GitHub Actions to the latest versions. | [gh-actions-update Documentation](../docs/gh-actions-update.md) |
| LogTools | A logging wrapper utility that can be wrapped around shell commands or used as a dropin replacement for the python logging library. It provides a simple way of presenting user friendly logging. It features styles, simple message only logging, method state and command state based logging. | [LogTools Documentation](../docs/logtools.md) |
| push | Utility that automates and standardises the pre-commit, lint, and commit message generation process. It enforces the best practice Conventional Commit standard, ensuring that your project has a consistent way of documenting changes and releases. | [push Documentation](../docs/push.md) |
| gh_pr_gen_title | Entrypoint that generates a PR title based on the PR diff. | [gh_pr_gen_title Documentation](../docs/entrypoint_pr_gen_title.md) |
| gh_pr_gen_summary | Entrypoint that generates a PR summary based on the PR diff. | [gh_pr_gen_summary Documentation](../docs/entrypoint_pr_gen_summary.md) |
| gh_pr_gen_context | Entrypoint that generates a PR context/reason based on the PR diff. | [gh_pr_gen_context Documentation](../docs/entrypoint_pr_gen_context.md) |

## Installation

To install the `klingon_tools` library use pip:

```sh
pip install klingon_tools
```


## Contributing

Contributions are welcome. Please open an issue to discuss your idea before making a change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
