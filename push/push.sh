#!/bin/bash
# Auto-commit script using OpenAI API for generating commit messages
# Copyright David Hooton 2024
# This script automates the process of generating commit messages based on staged changes,
# committing those changes, and handling file changes in a git repository. It utilizes
# the OpenAI API to generate commit messages following the Conventional Commits standard.
# It is divided into functions to improve maintainability and ease of understanding.
# Functions:
# - generate_commit_message: Generates a commit message using the OpenAI API.
# - handle_changed_files: Handles changed files by generating a commit message for staged changes and committing them.
# - main: The main function that orchestrates the script's flow.
# - check_environment_variables: Checks if required environment variables are
#   set.

# Define color variables
RED='\033[0;31m'
BOLD_RED='\033[1;31m'
GREEN='\033[0;32m'
GREEN_BOLD='\033[1;32m'
YELLOW='\033[1;33m'
BOLD_YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD_BLUE='\033[1;34m'
ORANGE='\033[0;33m'
BOLD_ORANGE='\033[1;33m'
NC='\033[0m' # No Color
WHITE_BOLD='\033[1;37m'
PRE_COMMIT_OK='\033[42m\033[34m'    # Green background with blue text
PRE_COMMIT_ERROR='\033[41m\033[97m' # Red background with white text
PRE_COMMIT_WARN='\033[43m\033[30m'  # Yellow background with black text
PRE_COMMIT_INFO='\033[46m\033[30m'  # Cyan background with black text

WIDTH=80 # Define the width for the output

# Set argument
export MESSAGE=$@

# Get root directory of git repo
ROOT_DIR=$(git rev-parse --show-toplevel)

TEMPLATE_FILE="$ROOT_DIR/scripts/.pushrc_template"
PUSH_CONFIG_FILE="$ROOT_DIR/.pushrc"
if [ ! -f "$PUSH_CONFIG_FILE" ]; then
    cp "$TEMPLATE_FILE" "$PUSH_CONFIG_FILE"
fi

if [ -z "$ENCRYPT_SECRETS" ]; then
    printf "${NC}%s${NC}\n" " ENCRYPT_SECRETS=${ENCRYPT_SECRETS:-false}"
else
    printf "${NC}%s${NC}\n" " ENCRYPT_SECRETS=$ENCRYPT_SECRETS"
fi

if [ -f "$PUSH_CONFIG_FILE" ]; then
    . "$PUSH_CONFIG_FILE"
else
    printf "${RED}%-${WIDTH}s${NC}\n" "Error: Configuration file .pushrc not found."
    exit 1
fi
printf "${GREEN}%-${WIDTH}s${NC}\n" "==============================================================================="
printf "${NC}%s${NC}\n" "Loaded .pushrc settings:"
if [ -z "$NO_COMMIT" ]; then
    printf "${NC}%s${NC}\n" " NO_COMMIT=${NO_COMMIT:-false}"
else
    printf "${NC}%s${NC}\n" " NO_COMMIT=$NO_COMMIT"
fi
if [ -z "$NO_FLUX" ]; then
    printf "${NC}%s${NC}\n" " NO_FLUX=${NO_FLUX:-false}"
else
    printf "${NC}%s${NC}\n" " NO_FLUX=$NO_FLUX"
fi
if [ -z "$NO_PRE_COMMIT" ]; then
    printf "${NC}%s${NC}\n" " NO_PRE_COMMIT=${NO_PRE_COMMIT:-false}"
else
    printf "${NC}%s${NC}\n" " NO_PRE_COMMIT=$NO_PRE_COMMIT"
fi
if [ -z "$NO_PUSH" ]; then
    printf "${NC}%s${NC}\n" " NO_PUSH=${NO_PUSH:-false}"
else
    printf "${NC}%s${NC}\n" " NO_PUSH=$NO_PUSH"
fi
if [ -z "$NO_SAVE_API" ]; then
    printf "${NC}%s${NC}\n" " NO_SAVE_API=${NO_SAVE_API:-false}"
else
    printf "${NC}%s${NC}\n" " NO_SAVE_API=$NO_SAVE_API"
fi
printf "${GREEN}%-${WIDTH}s${NC}\n" "==============================================================================="

function get_group_id() {
    # Set argument
    ARG=$@
    # Get group id from the file path in ARG and add it to the GROUP variable.
    # The group ID is the two numbers after the word "group-" in the file path.
    export GROUP=$(echo ${ARG} | perl -nle 'print for m/(?<=group-)[0-9]{2}/g' | sort -u)
    echo $GROUP
}

function get_app_name() {
    # Set argument
    ARG=$@
    # Get application name from file path in ARG and add it to the
    # APP variable. The application name is the word after the group id in the file path.
    export APP=$(echo ${ARG} | perl -nle 'print for m/(?<=group-[0-9]{2}\/)[a-z-]+/g' | sort -u)
    echo $APP
}

function run_precommit_all() {
    # Set exit to 0
    EXIT=0
    # Announce start of pre-commit run
    if [ "$#" -eq 1 ]; then
        printf "${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
        printf "${NC}%s${NC}\n" "Running pre-commit over all files"
        printf "${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
    else
        printf "${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
        printf "${NC}%s${NC}\n" "Running pre-commit over all files"
        printf "${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
    fi
    # Run pre-commit over the whole repository until it exits with zero
    local pre_commit_output
    local unencrypted_file
    local retry_count=0
    local max_retries=5
    local last_error=""
    while true; do
        SKIP=forbid_secrets pre-commit run --all-files
        EXIT=$?
        if [[ $EXIT -eq 0 ]]; then
            generate_precommit_logging "Pre-commit run finished" "Passed"
            break
        else
            # Check for unencrypted Kubernetes secrets
            pre_commit_output=$(pre-commit run --all-files 2>&1)
            echo "$pre_commit_output"
            if [[ "$pre_commit_output" =~ "Unencrypted Kubernetes secret detected in file:" ]]; then
                unencrypted_file=$(echo "$pre_commit_output" | grep -oP "(?<=Unencrypted Kubernetes secret detected in file: ).*")
                echo "Encrypting unencrypted secret in file: $unencrypted_file"
                "$ROOT_DIR/scripts/encrypt" "$unencrypted_file"
                git add "$unencrypted_file"
                # Remove any unencrypted versions of the file
                git rm --cached "$unencrypted_file.unencrypted" 2>/dev/null || true
                last_error=""
            else
                # If there are other errors, exit the loop
                if [[ -z "$last_error" || "$last_error" != "$pre_commit_output" ]]; then
                    last_error="$pre_commit_output"
                    retry_count=0
                fi
                ((retry_count++))
                if [[ $retry_count -ge $max_retries ]]; then
                    printf "${RED}%-${WIDTH}s${NC}\n" "==============================================================================="
                    echo " Pre-commit failed to fix the issue after $max_retries attempts."
                    echo " Here is the error:"
                    echo "$pre_commit_output"
                    printf "${RED}%-${WIDTH}s${NC}\n" "==============================================================================="
                    exit 1
                fi

                generate_precommit_logging "Attempting to fix the issue." "Retry $retry_count/$max_retries"

                if [[ -z "$last_error" || "$last_error" != "$pre_commit_output" ]]; then
                    last_error="$pre_commit_output"
                    retry_count=0
                fi
                ((retry_count++))
                if [[ $retry_count -ge $max_retries ]]; then
                    printf "${RED}%-${WIDTH}s${NC}\n" "==============================================================================="
                    echo " Pre-commit failed to fix the issue after $max_retries attempts."
                    echo " Here is the error:"
                    echo "$pre_commit_output"
                    printf "${RED}%-${WIDTH}s${NC}\n" "==============================================================================="
                    exit 1
                fi

                generate_precommit_logging "Attempting to fix the issue." "Retry $retry_count/$max_retries"

            fi
        fi
    done
}

function flux_reconcile() {
    # Set argument
    CHANGED_FILES=$@

    # Announce flux reconciliation
    printf "${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
    printf "${NC}%s${NC}\n" " Reconciling flux source"
    printf "${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
    # Reconcile flux source
    flux reconcile source git flux-system

    # Announce flux reconciliation
    printf "${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
    printf "${NC}%s${NC}\n" " Reconciling flux kustomization"
    printf "${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
    # Reconcile flux kustomization
    flux reconcile kustomization flux-system

    # Get list of changed kustomization names by iterating through the changed
    # files and extracting the unique list of kustomization names. To get the
    # kustomizations to reconcile inspect the file names as follows:
    #   - The file name is apps/group-00/cluster-config/ks-cluster-config.yaml
    #   - This makes the GROUP ID "00"
    #   - This makes the APP NAME "cluster-config"
    #   - Therefore the kustomization name is "00-cluster-config"
    # If the GROUP is ROOT then skip reconciliation of the kustomization
    # If the APP is kustomization then skip reconciliation of the kustomization
    for FILE in ${CHANGED_FILES[@]}; do
        # Announce file being processed
        generate_precommit_logging "Processing file:" "$FILE"
        # Get group id from file path
        GROUP=$(get_group_id $FILE)
        # If GROUP is empty set it to ROOT
        if [ -z $GROUP ]; then
            GROUP=ROOT
        fi

        # Announce Group
        generate_precommit_logging "Processing group:" "$GROUP"

        # Get application name from file path
        APP=$(get_app_name $FILE)
        # If APP is empty then set it to $PROJECT
        if [ -z $APP ]; then
            APP=$PROJECT
        fi

        # Announce application if $APP is defined
        if [ ! -z $APP ]; then
            generate_precommit_logging "Application:" "$APP"
        else
            generate_precommit_logging "Application not set" "ERROR "
        fi

        # If the GROUP is not ROOT and the APP is not kustomization then
        # reconcile the kustomization
        if [ $GROUP != "ROOT" ] && [ $APP != "kustomization" ]; then
            generate_precommit_logging "Reconciling kustomization" "$GROUP-$APP"
            echo
            # Reconcile the kustomization
            flux reconcile kustomization $GROUP-$APP
        else
            generate_precommit_logging "Skipping reconciliation of kustomization $GROUP-$APP" "SKIPPING"
        fi
    done
}

function check_environment_variables() {
    # Ensure the OPENAI_API_KEY environment variable is set before running the script.
    if [ -z "$OPENAI_API_KEY" ]; then
        generate_precommit_logging "OPENAI_API_KEY environment variable is not set" "ERROR "
        exit 1
    fi
}

function generate_commit_message() {
    local commit_message=""
    local attempt=1
    local max_attempts=5

    while [[ -z "$commit_message" && $attempt -lt $max_attempts ]]; do
        case $attempt in
            1) sleep 0 ;;  # No wait before the first attempt
            2) echo "Waiting 3 seconds before retrying..."; sleep 3 ;;
            3) echo "Waiting 6 seconds before retrying..."; sleep 6 ;;
            4) echo "Waiting 12 seconds before retrying..."; sleep 12 ;;
            5) echo "Waiting 24 seconds before retrying..."; sleep 24 ;;
        esac
        ((attempt++))

        # Generates a commit message using the OpenAI API based on staged git diffs.
        local staged_diffs=$(git --no-pager diff --staged --patch-with-stat)

        # Prepare the prompt for OpenAI GPT-3.5-turbo
        if [ -z "$staged_diffs" ]; then
            generate_precommit_logging "No staged changes to generate commit message for." "WARNING"
            return
        fi

        local role_system_content="Generate a commit message based solely on the staged diffs provided, ensuring accuracy and relevance to the actual changes.
        Avoid adding speculative or unnecessary footers, such as references to non-existent issues. You must adhere to the conventional commits standard. The commit message should:
     - Clearly specify the type of change (feat, fix, build, etc.).
     - Clearly specify the scope of change.
     - Describe the purpose and actual detail of the change with clarity.
     - Use bullet points for the body when more than one item is discussed.
     - You MUST follow the Conventional Commits standardized format:

    <type>(<scope>): <description>
    [optional body]
    [optional footer/breaking changes]


    Types include: feat, fix, build, ci, docs, style, refactor, perf, test, chore, etc.
    Ensure the message is factual, based on the provided diffs, and free from any speculative or unnecessary content."

        local role_user_content="Generate a git commit message based on these diffs (git --no-pager diff --patch-with-stat):
        \"${staged_diffs}\""

        # Call OpenAI API to generate commit message
        local role_system_content_encoded=$(echo "$role_system_content" | jq -sRr @uri)
        if [[ "$role_system_content_encoded" == *"jq: error"* ]]; then
            generate_precommit_logging "Error encoding role_system_content with jq: $role_system_content_encoded" "ERROR "
            exit 1
        fi
        local role_user_content_encoded=$(echo "$role_user_content" | jq -sRr @uri)
        if [[ "$role_user_content_encoded" == *"jq: error"* ]]; then
            generate_precommit_logging "Error encoding role_user_content with jq: $role_user_content_encoded" "ERROR "
            exit 1
        fi

        commit_message=$(
            curl -s -X POST "https://api.openai.com/v1/chat/completions" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $OPENAI_API_KEY" \
                -d "{
                    \"model\": \"gpt-3.5-turbo\",
                    \"messages\": [
                        {
                            \"role\": \"system\",
                            \"content\": \"$role_system_content_encoded\"
                        },
                        {
                            \"role\": \"user\",
                            \"content\": \"$role_user_content_encoded\"
                        }
                    ]
                }"
        )

        # Check if commit_message is empty or contains an error
        if [[ -z "$commit_message" || "$commit_message" == *"error"* ]]; then
            echo "Failed to generate commit message. Attempt $attempt of $max_attempts."
            commit_message=""
        fi
    done

    if [[ -z "$commit_message" ]]; then
        generate_precommit_logging "Failed to generate commit message after $max_attempts attempts." "ERROR "
        exit 1
    fi

    if [ "$NO_SAVE_API" != "true" ]; then
        # Save the API responses to a directory called .openai if it doesn't exist,
        # create it. The responses should be saved in files named in the following
        # format: .openai/YYYYMMDDHHMMSS-{system_fingerprint}-{finish_reason}.json
        if [ ! -d "$ROOT_DIR/.openai" ]; then
            mkdir -p "$ROOT_DIR/.openai"
        fi

        # Save the API response to a file
        local timestamp=$(date "+%Y%m%d%H%M%S")
        # Extract system_fingerprint and finish_reason from the API response
        local system_fingerprint=$(echo "$commit_message" | jq -r '.choices[0].system.system_fingerprint' 2>&1)
        if [[ "$system_fingerprint" == *"jq: error"* ]]; then
            generate_precommit_logging "Error extracting system_fingerprint with jq: $system_fingerprint" "ERROR "
            exit 1
        fi
        local finish_reason=$(echo "$commit_message" | jq -r '.choices[0].finish_reason')
        if [[ "$finish_reason" == *"jq: error"* ]]; then
            generate_precommit_logging "Error extracting finish_reason with jq: $finish_reason" "ERROR "
            exit 1
        fi
        # Save the API response to a file
        echo "$commit_message" >"$ROOT_DIR/.openai/${timestamp}-${system_fingerprint}-${finish_reason}.json"
    fi

    # Extract the generated commit message from the API response
    commit_message=$(echo "$commit_message" | jq -r '.choices[0].message.content' | sed 's/+/ /g;s/%\(..\)/\\x\1/g;')

    if [[ "$commit_message" == *"jq: error"* ]]; then
        generate_precommit_logging "Error extracting the final commit_message with jq: $commit_message" "ERROR "
        exit 1
    fi

    # If finish_reason is not stop then print a warning message and exit 1
    #if [ "$finish_reason" != "stop" ]; then
    #    generate_precommit_logging "The API response did not finish successfully. Exiting." "ERROR "
    #    exit 1
    #fi

    # Return the generated commit message
    printf "$commit_message"
}

function git_pull_rebase_precommit() {
    # Stash any unstaged changes before pulling
    git stash -u

    # Perform a git pull with rebase
    if ! git pull --rebase; then
        generate_precommit_logging "Error pulling changes from the remote repository." "ERROR "
        git stash pop
        exit 1
    fi

    # Pop the stash to restore the unstaged changes
    git stash pop

    # Run pre-commit over the whole repository until it exits with zero
    if [ "$NO_PRE_COMMIT" != "true" ]; then
        run_precommit_all
    fi
}

# Function: generate_precommit_logging
#
# Description:
# This function generates a formatted log message for pre-commit hooks. It takes a message and a status as input parameters.
# The function splits the message into words and formats them into lines with a maximum length of 69 characters.
# If a word exceeds the maximum length, it is split into multiple lines.
# The formatted lines are then concatenated with dots and the status to create the final log message.
#
# Parameters:
# - message: The message to be logged.
# - status: The status of the pre-commit hook.
#
# Output:
# The formatted log message.
#
# Example usage:
# generate_precommit_logging "Commit message" "PASSED"
#
# Returns:
# Commit message....................................................PASSED
#

function generate_precommit_logging() {
    local message="$1" status="$2" max_len=69 output="" current_line="" IFS=$' \n'
    local total_len=79               # Total length of the output line including status and dots
    local status_len=$((${#status})) # Length of the status message plus color codes
    local dots_len                   # Length of dots to be added
    local first_line=true            # Flag to check if it's the first line of output

    # Function to add a word to the current line
    add_word() {
        local word=$1
        # Check if adding the word exceeds the maximum line length
        if [[ $((${#current_line} + ${#word} + 1)) -gt $max_len ]]; then
            # If the current line is not empty, add it to the output
            if [[ -n "$current_line" ]]; then
                output+="${current_line}\n"
                current_line=""
            fi
            # If the word itself exceeds the maximum length, split it
            while [[ ${#word} -gt $max_len ]]; do
                output+="${word:0:$max_len}\n"
                word="${word:$max_len}"
            done
            current_line="$word"
        else
            # Add the word to the current line
            current_line+="${current_line:+ }$word"
        fi
    }

    # Loop through the words in the message and add them to the current line
    # Split the message into words and process each word
    for word in $message; do add_word "$word"; done

    # Calculate the length of dots required for padding
    dots_len=$((total_len - ${#current_line} - status_len))
    [[ $dots_len -lt 1 ]] && dots_len=1 # Ensure at least one dot

    # Add the final line to the output with padding and status
    if [[ "$status" == "OK" || "$status" == "Passed" || "$status" == "Added " || "$status" == "INFO" ]]; then
        output+="${current_line}$(printf '.%.0s' $(seq 1 $dots_len))${PRE_COMMIT_OK}$status${NC}"
    elif [[ "$status" == "ERROR " ]]; then
        output+="${current_line}$(printf '.%.0s' $(seq 1 $dots_len))${PRE_COMMIT_ERROR}$status${NC}"
    elif [[ "$status" == "SKIPPING" ]]; then
        output+="${current_line}$(printf '.%.0s' $(seq 1 $dots_len))${PRE_COMMIT_INFO}$status${NC}"
    elif [[ "$status" == "WARNING" || "$status" == "Retry "* ]]; then
        output+="${current_line}$(printf '.%.0s' $(seq 1 $dots_len))${PRE_COMMIT_WARN}$status${NC}"
    else
        output+="${current_line}$(printf '.%.0s' $(seq 1 $dots_len))$status"
    fi

    # Print the formatted output
    echo -e "$output"
}

function git_push_changes() {
    if [ "$NO_PUSH" != "true" ]; then
        if ! git pull --rebase && git push; then
            generate_precommit_logging "Failed to pull and push changes to the remote repository." "ERROR "
            exit 1
        else
            generate_precommit_logging "Changes successfully pushed to the remote repository." "OK"
        fi
    fi
}

function handle_changed_files() {
    local specific_files=("$@")
    local max_requeue_attempts=5
    local max_failure_attempts=5
    # Generate a commit message for staged files and run pre-commit on them
    if [ ${#specific_files[@]} -gt 0 ]; then
        CHANGED_FILES=("${specific_files[@]}")
    else
        CHANGED_FILES=($(git status --porcelain | sed 's/^...//'))

        # Figure out which files have not been committed yet
        STAGED_FILES=($(git diff --name-only --cached))

        # Figure out which commits have not been pushed
        UNPUSHED_COMMITS=($(git log @{u}.. --oneline | awk '{ print $1 }'))

        # Print the information
        printf "${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
        printf "LOCAL GIT BRANCH STATE (START)\n"
        printf "${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
        printf " CHANGED FILES:                                                             ${#CHANGED_FILES[@]}\n"
        printf " STAGED FILES:                                                              ${#STAGED_FILES[@]}\n"
        printf " COMMITS TO PUSH:                                                           ${#UNPUSHED_COMMITS[@]}\n"
        printf "${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="

        # If there are no changed files and no staged files but there are commits to push, skip everything else and push to git
        if [ ${#CHANGED_FILES[@]} -eq 0 ] && [ ${#STAGED_FILES[@]} -eq 0 ] && [ ${#UNPUSHED_COMMITS[@]} -gt 0 ]; then
            git_push_changes
            return
        fi

        # If there are no changed files, staged files, or unpushed commits, exit
        # the function with a message that there are no changes to commit or push.
        if [ ${#CHANGED_FILES[@]} -eq 0 ] && [ ${#STAGED_FILES[@]} -eq 0 ] && [ ${#UNPUSHED_COMMITS[@]} -eq 0 ]; then
            # If there are no changes to commit or push, generate a skipping
            # message and exit the function.
            LOG_MSG=$(generate_precommit_logging "No changes to commit or push." "SKIPPING")

            # Print the message
            printf "%b\n" "$LOG_MSG"

            # Exit the function
            return
        fi

        # Update the local repository with the remote repository, autostashing any
        # local changes and rebasing the local changes on top of the remote changes.
        git_pull_rebase_precommit

        # Make sure the changes are safe to push with pre-commit
        # Process each changed file individually
        for FILE in "${CHANGED_FILES[@]}"; do
            if [ "$ENCRYPT_SECRETS" == "true" ]; then
                "$ROOT_DIR/scripts/encrypt-decrypt.sh" "$ROOT_DIR/$FILE"
            fi
            git add "$ROOT_DIR/$FILE"
            run_precommit_all
            local commit_msg=$(generate_commit_message)
            local file_index=$(printf '%s\n' "${CHANGED_FILES[@]}" | grep -n -x "$FILE" | cut -d: -f1)
            requeue_count[$file_index]=$((requeue_count[$file_index]+1))
            if [ -z "$commit_msg" ]; then
                failure_counts["$FILE"]=$((failure_counts["$FILE"]+1))
                if [ ${failure_counts["$FILE"]} -ge $max_failure_attempts ]; then
                    FAILED+=("$FILE")
                    generate_precommit_logging "File $FILE failed to generate commit message after $max_failure_attempts attempts." "ERROR "
                    continue
                elif [ ${requeue_count[$file_index]} -le $max_requeue_attempts ]; then
                    generate_precommit_logging "No commit message generated for $FILE. Re-queuing..." "WARNING"
                    requeue_files+=("$FILE")
                fi
                generate_precommit_logging "No commit message generated for $FILE. Re-queuing..." "WARNING"
                requeue_files+=("$FILE")
            elif [ ${requeue_count[$file_index]} -gt $max_requeue_attempts ]; then
                generate_precommit_logging "Maximum re-queue attempts reached for $FILE." "ERROR "
                generate_precommit_logging "No commit message generated for $FILE." "ERROR "
            else
                printf "\n${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
                printf "${NC}%s${NC}\n" "GENERATED COMMIT MESSAGE FOR $FILE:"
                printf "$commit_msg" | fold -s -w 79
                printf "\n${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
                git commit -m "$commit_msg"
            fi
        done

        if [ ${#requeue_files[@]} -gt 0 ]; then
            printf "\n${BLUE}%-${WIDTH}s${NC}\n" "Re-queuing files for processing..."
            handle_changed_files "${requeue_files[@]}"
        fi
        # Stage changed files in git
        for FILE in "${CHANGED_FILES[@]}"; do
            # Stage the file in git
            git add "$ROOT_DIR/$FILE"
            if [ $? -eq 0 ]; then
                # If the git add exits clean use generate_precommit_logging to generate
                # the success message
                generate_precommit_logging "Adding $FILE to git" "Added "
            else
                # If the git add exits with an error use generate_precommit_logging
                # to generate the error message
                generate_precommit_logging "Adding $FILE to git" "ERROR "
            fi
        done

        if [ "$NO_COMMIT" != "true" ] && [ -z "$commit_msg" ]; then
            # Generate a conventional commit message for staged files
            local commit_msg=$(generate_commit_message)
            if [ -z "$commit_msg" ]; then
                generate_precommit_logging "No commit message generated." "ERROR "
                return
            fi

            # Print the generated commit message
            printf "\n${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="
            printf "${NC}%s${NC}\n" "GENERATED COMMIT MESSAGE:"
            printf "$commit_msg" | fold -s -w 79
            printf "\n${BLUE}%-${WIDTH}s${NC}\n" "==============================================================================="

            # Commit the changes with the generated commit message
            git commit -m "$commit_msg"

            git_push_changes
        fi

    fi

    # Once more push just in case
    git_push_changes
}

function main() {
    cd "$ROOT_DIR" || exit
    check_environment_variables
    if [ "$#" -eq 0 ]; then
        handle_changed_files
    else
        for specific_file in "$@"; do
            handle_changed_files "$specific_file"
        done
    fi
}

# Find and encrypt all unencrypted secrets in the repository
# Get project name from git repo
PROJECT=$(basename "$ROOT_DIR")

# Function to detect the OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &>/dev/null; then
            echo "ubuntu"
        else
            echo "unsupported_linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unsupported_os"
    fi
}

OS=$(detect_os)

# Make sure pre-commit is installed
if ! command -v pre-commit &>/dev/null; then
    echo "pre-commit could not be found, installing it."
    if [ "$OS" == "macos" ]; then
        HOMEBREW_NO_AUTO_UPDATE=true brew install pre-commit
    elif [ "$OS" == "ubuntu" ]; then
        sudo apt update && sudo apt install -y pre-commit
    else
        echo "Unsupported OS for automatic installation of pre-commit."
        exit 1
    fi
fi

if [ "$NO_FLUX" != "true" ]; then
    # Make sure flux is installed
    if ! command -v flux &>/dev/null; then
        echo "flux could not be found, installing it."
        if [ "$OS" == "macos" ]; then
            HOMEBREW_NO_AUTO_UPDATE=true brew install flux
        elif [ "$OS" == "ubuntu" ]; then
            sudo curl -s https://fluxcd.io/install.sh | sudo bash
        else
            echo "Unsupported OS for automatic installation of flux."
            exit 1
        fi
    fi
fi

# Find changed files, get them into git, generate a meaningful commit message,
# make sure they are safe to push and push them
main $@

exit 0
declare -A failure_counts
FAILED=()

    if [ ${#FAILED[@]} -gt 0 ]; then
        printf "\n${RED}%-${WIDTH}s${NC}\n" "Files that failed to generate commit messages:"
        for failed_file in "${FAILED[@]}"; do
            printf "${RED}%s${NC}\n" "$failed_file"
        done
    fi
