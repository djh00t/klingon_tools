#!/bin/bash

# Extract the new version from package.json
NEW_VERSION=$(grep '"version":' package.json | sed 's/.*"version": "\(.*\)",/\1/')
echo "New version extracted: $NEW_VERSION"

# Update the version in pyproject.toml
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    sed -i '' -e "s/^version = \".*\"/version = \"$NEW_VERSION\"/" ./pyproject.toml
else
    echo "Detected Linux"
    sed -i'' -e "s/^version = \".*\"/version = \"$NEW_VERSION\"/" ./pyproject.toml
fi

# Update the version in package.json
jq --arg new_version "$NEW_VERSION" '.version = $new_version' package.json > tmp.$$.json && mv tmp.$$.json package.json

# Run semantic-release
echo "Running semantic-release..."
npx semantic-release

# If semantic-release was successful, commit the changes
if [ $? -eq 0 ]; then
    git add pyproject.toml
    git commit -m "chore: update pyproject.toml to $NEW_VERSION [skip ci]"
    git push
else
    echo "semantic-release failed"
fi
