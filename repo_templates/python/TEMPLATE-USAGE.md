# Template Usage

## Installation
1. Clone the repository from `https://github.com/djh00t/klingon_tools/repo_templates/python/`.
2. Navigate to the project directory.
3. Install the necessary dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. Run pre-commit hooks:
    ```sh
    pre-commit install
    pre-commit run --all-files
    ```
2. Use the `make update` command to keep the base template and pre-commit hooks up to date:
    ```sh
    make update
    ```

## Updating the Template
1. Run the `make update` command to fetch the latest changes:
    ```sh
    make update
    ```
2. Review and merge the generated PR for the updates.

## Customizing the Template
1. To include project-specific configurations in the `.pre-commit-config.yaml`, add your custom hooks to the file.
2. Ensure your custom configurations are not overwritten by the `make update` command by merging them appropriately.
