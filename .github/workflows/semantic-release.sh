#!/bin/bash

echo "Running semantic-release..."
npx semantic-release

# If semantic-release was successful, update the version in pyproject.toml
if [ $? -eq 0 ]; then
    NEW_VERSION=$(grep '"version":' ./package.json | sed 's/^  "version": "\(.*\)",$/\1/')
    echo "New version extracted: $NEW_VERSION"
    echo "Updating pyproject.toml with new version: $NEW_VERSION"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS"
        sed -i '' -e "s/^version = \".*\"/version = \"$NEW_VERSION\"/" ./pyproject.toml
    else
        echo "Detected Linux"
        sed -i'' -e "s/^version = \".*\"/version = \"$NEW_VERSION\"/" ./pyproject.toml
    fi
    echo "New version extracted: $NEW_VERSION"
    echo "Updating pyproject.toml with new version: $NEW_VERSION"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS"
        sed -i '' -e "s/^version = \".*\"/version = \"$NEW_VERSION\"/" ./pyproject.toml
    else
        echo "Detected Linux"
        sed -i'' -e "s/^version = \".*\"/version = \"$NEW_VERSION\"/" ./pyproject.toml
    fi
echo "Running semantic-release..."
npx semantic-release

# If semantic-release was successful, update the version in pyproject.toml
if [ $? -eq 0 ]; then
    NEW_VERSION=$(grep '"version":' package.json | sed 's/.*"version": "\(.*\)",/\1/')
    echo "New version extracted: $NEW_VERSION"
    echo "Updating pyproject.toml with new version: $NEW_VERSION"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Detected macOS"
        sed -i '' -e "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
        echo "Updated pyproject.toml on macOS"
    else
        echo "Detected Linux"
        sed -i'' -e "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
        echo "Updated pyproject.toml on Linux"
    fi
    git add pyproject.toml
    git commit -m "chore: update pyproject.toml to $NEW_VERSION [skip ci]"
    git push
else
    echo "semantic-release failed"
fi
    git add pyproject.toml
    git commit -m "chore: update pyproject.toml to $NEW_VERSION [skip ci]"
    git push
fi
