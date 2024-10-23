#!/bin/bash

# Setup variables
export BRANCH_BASE=$WORKFLOW_STAGE
echo "BRANCH_BASE=$BRANCH_BASE" >> $GITHUB_ENV

export WORKFLOW_STAGE_CAP=$(echo $WORKFLOW_STAGE | awk '{print toupper(substr($0, 1, 1)) tolower(substr($0, 2))}')
echo "WORKFLOW_STAGE_CAP=$WORKFLOW_STAGE_CAP" >> $GITHUB_ENV

export BRANCH_CURRENT=$(git rev-parse --abbrev-ref HEAD)
echo "BRANCH_CURRENT=$BRANCH_CURRENT" >> $GITHUB_ENV

# Setup Git and GitHub CLI
git config --global user.email "github-actions[bot]@users.noreply.github.com"
git config --global user.name "github-actions[bot]"

# Authenticate GitHub CLI
echo "$GH_TOKEN" | gh auth login --with-token

# Check for PR
PR_EXISTS=$(gh pr list --head $BRANCH_CURRENT --json number --jq '.[0].number' || echo "")
echo "PR_EXISTS=$PR_EXISTS" >> $GITHUB_ENV

if [ -n "$PR_EXISTS" ]; then
    PR_NUMBER=$(gh pr list --head $BRANCH_CURRENT --json number --jq '.[0].number')
    echo "PR_NUMBER=$PR_NUMBER" >> $GITHUB_ENV

    PR_URL=$(gh pr view $PR_NUMBER --json url --jq '.url')
    echo "PR_URL=$PR_URL" >> $GITHUB_ENV

    PR_TITLE=$(gh pr view $PR_NUMBER --json title --jq '.title')
    echo "PR_TITLE=$PR_TITLE" >> $GITHUB_ENV
fi
