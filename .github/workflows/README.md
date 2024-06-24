# GitHub Workflows

This directory contains the GitHub Actions workflows for this repository. Below is a brief description of each workflow:

## auto-pr.yaml
This workflow automatically creates a pull request when changes are pushed to a specific branch.

## deploy.yaml
This workflow handles the deployment process. It is triggered when changes are pushed to the main branch.

## release-drafter.yaml
This workflow drafts a new release based on the merged pull requests. It is triggered when changes are pushed to the main branch.

## run-tests.yaml
This workflow runs the test suite to ensure that the codebase is functioning correctly. It is triggered on pull requests and pushes to the main branch.
