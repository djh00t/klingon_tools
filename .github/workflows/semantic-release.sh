#!/bin/bash

# Extract the new version from package.json
NEW_VERSION=$(grep '"version":' package.json | sed 's/.*"version": "\(.*\)",/\1/')
echo "New version extracted: $NEW_VERSION"

# Update the version in pyproject.toml
poetry version $NEW_VERSION

# Update the version in package.json
jq --arg new_version "$NEW_VERSION" '.version = $new_version' package.json > tmp.$$.json && mv tmp.$$.json package.json

# Update the version in klingon_tools/__init__.py
sed -i '' "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" klingon_tools/__init__.py
echo "Running semantic-release..."
npx semantic-release

# If semantic-release was successful, commit the changes to a new branch
if [ $? -eq 0 ]; then
    git checkout -b release-v$NEW_VERSION
    git add pyproject.toml
    git commit -m "chore: update version to $NEW_VERSION [skip ci]"
    git push origin release-v$NEW_VERSION
else
    echo "semantic-release failed"
fi
