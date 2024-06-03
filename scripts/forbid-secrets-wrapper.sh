#!/bin/bash

# Path to the pre-commit hook executable for forbid-secrets
FORBID_SECRETS_PATH=$(command -v forbid-secrets)  # Adjust this as necessary

# Run forbid-secrets and capture its exit code
$FORBID_SECRETS_PATH "$@"
EXIT_CODE=$?

# Check if forbid-secrets failed
if [ $EXIT_CODE -ne 0 ]; then
  echo "forbid-secrets failed. Attempting to encrypt sensitive files..."

  # Assuming the failed file paths are accessible, loop through them
  # This is a placeholder loop, you'll need to adjust it based on your actual needs
  for file in "$@"; do
    # Run your encrypt-decrypt script with each file
    ./scripts/encrypt-decrypt.sh "$file"
  done

  # Optionally, retry forbid-secrets or handle the error as needed
  # $FORBID_SECRETS_PATH "$@"
fi

exit $EXIT_CODE
