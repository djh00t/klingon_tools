#!/bin/bash

# Run semantic-release
npx semantic-release

# If semantic-release was successful, update the version in pyproject.toml
if [ $? -eq 0 ]; then
    NEW_VERSION=$(grep '"version":' package.json | sed 's/.*"version": "\(.*\)",/\1/')
    echo "Updating pyproject.toml with new version: $NEW_VERSION"
    sed -i "s/version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
    git add pyproject.toml
    git commit -m "chore: update pyproject.toml to $NEW_VERSION [skip ci]"
    git push
fi
