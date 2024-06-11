# Makefile
update:
    @echo "Updating base template and pre-commit hooks..."
    @curl -o .pre-commit-config.yaml https://raw.githubusercontent.com/djh00t/klingon_tools/repo_templates/python/.pre-commit-config.yaml
    @echo "Applying project-specific configurations..."
    @# Add logic to merge or overwrite configurations here
    @pre-commit autoupdate