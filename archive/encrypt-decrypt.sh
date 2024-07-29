#!/bin/bash
###
### Encrypt K8S Files with Secrets
###
# Add files from arguments to ARGS array
ARGS_SCRIPT_0=($@)

# Get root directory of git repo
ROOT_DIR=$(git rev-parse --show-toplevel)

# Capture the name used to call this script
SCRIPT_NAME=$(basename $0)
# Uppercase version of SCRIPT_NAME
SCRIPT_NAME_UPPER=$(echo $SCRIPT_NAME | tr '[:lower:]' '[:upper:]')
echo "==============================================================================="
echo " Running $SCRIPT_NAME"
echo "==============================================================================="

# Set DEBUG to 2 (WARN) by default
export DEBUG=2

# Loop through ${ARGS_SCRIPT_0[@]} and sort arguments into ARGS_SCRIPT array
# and DEBUG boolean variable. If the argument is -d or --debug, set DEBUG to 1.
# If the argument is not -d or --debug, add it to the ARGS_SCRIPT array.
for arg in "${ARGS_SCRIPT_0[@]}"; do
    # Check if $arg is -d or --debug
    if [[ $arg == "-d" ]] || [[ $arg == "--debug" ]]; then
        # $arg is -d or --debug, set DEBUG to 1
        #echo " DEBUG:   DEBUG is active."
        export DEBUG=3
    else
        # $arg is not -d or --debug, add it to the ARGS_SCRIPT array
        ARGS_SCRIPT+=("$arg")
    fi
done


# Check if $ARGS_SCRIPT is empty, if it is, exit showing help message
if [ -z "$ARGS_SCRIPT" ]; then
    echo "ERROR: No arguments provided"
    echo "Usage: $SCRIPT_NAME <file1> <file2> <file3> ..."
    echo "You can use literal file paths, wildcards and regex"
    echo "Example: $SCRIPT_NAME ./k8s/* ./k8s/**/*"
    exit 1
fi

# Load .pushrc configuration
PUSH_CONFIG_FILE="$ROOT_DIR/.pushrc"
if [ -f "$PUSH_CONFIG_FILE" ]; then
    . "$PUSH_CONFIG_FILE"
else
    echo "Error: Configuration file .pushrc not found."
    exit 1
fi


# Get the age public key
KEY_AGE_PUBLIC=$(cat $ROOT_DIR/.age.pub)
# Get the age private key
KEY_AGE_PRIVATE=$(cat $ROOT_DIR/age.agekey | grep -v '#')
# Get the age private key file
KEY_AGE_PRIVATE_FILE="$ROOT_DIR/age.agekey"

function debug(){
    # Capture the users DEBUG_LEVEL setting
    DEBUG_LEVEL=$DEBUG

    # If DEBUG_LEVEL is not set, set it to 2 (WARN)
    if [ -z "$DEBUG_LEVEL" ]; then
        DEBUG_LEVEL=2
    fi

    # Capture the DEBUG_MSG_LEVEL
    DEBUG_MSG_LEVEL=$1

    # If DEBUG_MSG_LEVEL is not numeric, set it to 2 (ERROR)
    if ! [[ $DEBUG_MSG_LEVEL =~ ^[0-9]+$ ]]; then
        DEBUG_MSG_LEVEL=2
    fi

    # Capture the rest of the arguments in DEBUG_MSG
    shift
    DEBUG_MSG="$@"

    # There are 5 user DEBUG_LEVEL settings:
    #   0 - INFO and FATAL level messages only
    #   1 - WARN, INFO and FATAL level messages only
    #   2 - ERROR, WARN, INFO and FATAL level messages only
    #   3 - DEBUG, ERROR, WARN, INFO and FATAL level messages only
    #   4 - TRACE, DEBUG, ERROR, WARN, INFO and FATAL level messages

    # There are 6 DEBUG_MSG_LEVEL settings:
    #   0 - INFO level messages
    #   1 - WARN level messages
    #   2 - ERROR level messages
    #   3 - DEBUG level messages
    #   4 - TRACE level messages
    #   5 - FATAL level messages

    # Define message level strings and corresponding colors
    LEVEL_STR=("INFO" "WARN" "ERROR" "DEBUG" "TRACE" "FATAL")
    COLOR_CODES=("\e[1;32m" "\e[1;33m" "\e[1;31m" "\e[1;34m" "\e[1;38;5;208m" "\e[1;3;31m")

    # Get the current date and time in syslog format
    CURRENT_DATE=$(date +"%b %d %H:%M:%S")

    # Reset color
    RESET_COLOR="\e[0m"

    # Logic to print log messages in syslog format with color
    if [ "$DEBUG_LEVEL" -ge "$DEBUG_MSG_LEVEL" ] || [ "$DEBUG_MSG_LEVEL" -eq 5 ]; then
        if [ "$DEBUG_MSG_LEVEL" -eq 5 ]; then
            printf "%s %s %b%s:%b\t%b%s%b\n" "$CURRENT_DATE" "$(hostname)" "${COLOR_CODES[5]}" "${LEVEL_STR[5]}" "$RESET_COLOR" "${COLOR_CODES[5]}" "$DEBUG_MSG" "$RESET_COLOR"
        else
            printf "%s %s %b%s:%b\t%s\n" "$CURRENT_DATE" "$(hostname)" "${COLOR_CODES[$DEBUG_MSG_LEVEL]}" "${LEVEL_STR[$DEBUG_MSG_LEVEL]}" "$RESET_COLOR" "$DEBUG_MSG"
        fi
    fi

}

function check_if_encrypted() {
    # Check if file is already encrypted
    # Store file path in CHECK_IF_ENC
    CHECK_IF_ENC_ARG=$1

    # Look for '- recipient: $KEY_AGE_PUBLIC' in file.
    # If found, return 1.
    # If not, return 0.
    grep -q -e "- recipient: $KEY_AGE_PUBLIC" $CHECK_IF_ENC_ARG
    if [ $? -eq 0 ]; then
        # File $CHECK_IF_ENC_ARG is encrypted.
        echo 1
        return 1
    else
        # File $CHECK_IF_ENC_ARG is not encrypted.
        echo 0
        return 0
    fi
}

function decrypt_file() {
    # Capture file path in DECRYPT_FILE_ARG
    DECRYPT_FILE_ARG=$1

    # Check if DECRYPT_FILE_ARG is encrypted or not using the
    # check_if_encrypted function. If function returns 1 then
    # it is encrypted, if it returns 0 then is is unencrypted.
    ENCRYPTED=$(check_if_encrypted $DECRYPT_FILE_ARG)

    # Check if file is encrypted
    if [ $ENCRYPTED -eq 1 ]; then
        # Announce file is encrypted
        debug 0 "File Status:   ENCRYPTED"
        debug 0 "Action:        DECRYPTING"

        # File is encrypted, decrypt it
        sops --decrypt --in-place $DECRYPT_FILE_ARG

        # Capture exit code in DEC_EXIT
        DEC_EXIT=$?

        debug 3 "Exit Code:     $DEC_EXIT"

        # Announce file is decrypted
        debug 0 "File Status:   DECRYPTED"
    else
        # File is not encrypted, skip it
        debug 0 "File Status:   DECRYPTED"
        debug 0 "Action:        SKIPPING"

    fi
}



function encrypt_file() {
    # Capture file path in ENCRYPT_FILE_ARG
    ENCRYPT_FILE_ARG=$1

    # Check if ENCRYPT_FILE_ARG is encrypted or not using the
    # check_if_encrypted function. If function returns 1 then
    # it is encrypted, if it returns 0 then is is unencrypted.
    ENCRYPTED=$(check_if_encrypted $ENCRYPT_FILE_ARG)

    # Check if file is encrypted
    if [ $ENCRYPTED -eq 1 ]; then
        # Announce file is encrypted
        debug 0 "File Status:   ENCRYPTED"
        debug 0 "Action:        SKIPPING"
        break
    else
        # Announce file is not encrypted
        debug 0 "File Status:   DECRYPTED"
        debug 0 "Action:        ENCRYPTING"

        # File is not encrypted, encrypt it
        sops --encrypt --in-place $ENCRYPT_FILE_ARG

        # Capture exit code in DEC_EXIT
        DEC_EXIT=$?

        debug 3 "Exit Code:     $DEC_EXIT"

        # Announce file is encrypted
        debug 0 "File Status:   ENCRYPTED"
    fi
}

function validate_file(){
    FILE=$@
    # Validate that $FILE is a file
    if [[ -f "$FILE" ]]; then
        debug 3 "Validate file:    $FILE"
        # Make sure value being added to FILES array is a valid file
        # name and doesn't have extra slashes or /./'s in it
        unset RESULT
        RESULT=$(echo "$FILE" | sed 's/\/\//\//g' | sed 's/\.\///g')
        debug 3 "RESULT:        $RESULT"
        FILES+=("$RESULT")
    else
        echo "File $FILE not found"
        break
    fi
}

function explode_wildcards(){
    WILD_VALUE=$@
    # Find values containing regex and bash wildcard values
    if [[ $WILD_VALUE =~ [\*\?\[\]\{\}\|] ]]; then # Change the if statement to match on the wildcard characters
        debug 3 "Validated:     Value "$WILD_VALUE" contains a wildcard or regex"

        # Find files represented by the wildcard/regex
        debug 0 "Checking:      Does regex/wildcard represent any valid files?"
        VALID_WILDCARDS=($(ls -A $WILD_VALUE 2> /dev/null))

        # If ${#VALID_WILDCARDS[@]} is greater than 0, then the wildcard/regex
        # represents at least one file otherwise it represents no files so exit
        # the script
        if [[ ${#VALID_WILDCARDS[@]} -gt 0 ]]; then
            debug 3 "Success:       Found ${#VALID_WILDCARDS[@]} files"
            for k in ${VALID_WILDCARDS[@]}; do
                debug 3 "Adding:        Adding file $PWD/$k"
                FILES+=("$PWD/$k")
            done
        else
            debug 3 "No Match:      Regex/wildcard represents no files, exiting."
        fi
    else
        debug 3 "No Match:      Value "$WILD_VALUE" does not contain a wildcard or regex, exiting."
    fi
}

function explode_directories(){
    DIR_VALUE="$1"
    debug 3 "DIR_VALUE:     $DIR_VALUE"

    if [[ -d "$DIR_VALUE" ]]; then
        debug 3 "Validated:     $DIR_VALUE is a directory"
        unset VALID_FILES
        declare -a VALID_FILES  # Declare an array

        # Using a while loop to read each line from the find command into the array
        while IFS= read -r line; do
            VALID_FILES+=("$line")
        done < <(find "$DIR_VALUE" -type f)

        if [[ "${#VALID_FILES[@]}" -gt 0 ]]; then
            debug 4 "Success:       Found ${#VALID_FILES[@]} files"
            for j in "${VALID_FILES[@]}"; do
                debug 4 "Adding:        Adding file $j"
                # Add $j to FILES array
                FILES+=("$j")
            done
        else
            debug 3 "No Match:      Directory contains no files, exiting."
        fi
    else
        debug 3 "No Match:      Value $DIR_VALUE is not a directory, exiting."
    fi
}

function value_router(){
    VALUE_ROUTER=$@
    # Decide if VALUE_ROUTER is a file, directory, wildcard, or regex and send it
    # to the appropriate function
    if [[ -f "$VALUE_ROUTER" ]]; then
        debug 0 "Routing:       $VALUE_ROUTER is a file"
        validate_file "$VALUE_ROUTER"
    elif [[ -d "$VALUE_ROUTER" ]]; then
        debug 0 "Routing:       $VALUE_ROUTER is a directory"
        explode_directories "$VALUE_ROUTER"
    elif [[ $VALUE =~ ^[[:alnum:].*/%]*$ ]]; then
        debug 0 "Routing:       $VALUE_ROUTER is a regex/wildcard value"
        explode_wildcards "$VALUE_ROUTER"
    fi
}

function handle_args() {
    # Initialize the FILES array.
    local FILES=()

    # Loop through all values in the ARGS_SCRIPT array and send them to the
    # appropriate function using the value_router
    for i in "${ARGS_SCRIPT[@]}"; do
        debug 3 "Processing:    $i"
        value_router "$i"
    done

    # Loop through the FILES array and remove any duplicate values
    debug 3 "Filtering:     Filtering FILES array based on .sops.yaml file"

    local REGEX_FILES=()
    # Get the path_regex value from the .sops.yaml file if it exists
    PATH_REGEX=$(yq e '.creation_rules[0].path_regex' .sops.yaml)

    # If PATH_REGEX isn't empty then loop through the FILES array and remove
    # any values that don't match the PATH_REGEX
    if [[ ! -z "$PATH_REGEX" ]]; then
        debug 3 "Path Regex:    $PATH_REGEX"
        for file in "${FILES[@]}"; do
            # Check if $file matches $PATH_REGEX
            if [[ $file =~ $PATH_REGEX ]]; then
                # $file matches $PATH_REGEX, add it to the FILES array
                debug 4 "Success:       $file"
                REGEX_FILES+=("$file")
            else
                # $file does not match $PATH_REGEX, skip it
                debug 4 "No Match:      $file"
            fi
        done
    else
        debug 3 "Path Regex:    No path_regex found in .sops.yaml file"
    fi

    # Calculate number of files in FILES array minus the number of files in
    # REGEX_FILES array
    FILTERED_FILES=$((${#FILES[@]} - ${#REGEX_FILES[@]}))

    # File handling stats
    debug 0 "Stats:         ${#FILES[@]} files in directory"
    debug 0 "Stats:         $((${#FILES[@]} - ${#REGEX_FILES[@]})) files filtered"
    debug 0 "Stats:         ${#REGEX_FILES[@]} files for processing"

    # Unset the FILES array
    unset FILES

    # Export the REGEX_FILES array values as a CSV string called FILES
    export FILES_CSV=$(IFS=, ; echo "${REGEX_FILES[*]}")
}

unset FILES

# Call handle_args function and store output in FILES array
handle_args 2> /dev/null

# Convert FILES_CSV CSV string to FILES array
IFS=',' read -r -a FILES <<< "$FILES_CSV"

# Set action to perform
ACTION=$SCRIPT_NAME

# Loop through FILES array and $ACTION all files referenced
for file in "${FILES[@]}"; do
    # Check if file is encrypted
    ENCRYPTED=$(check_if_encrypted $file)

    # If $ACTION is encrypt and file is not encrypted, encrypt it
    if [[ $ACTION == "encrypt" ]] && [[ $ENCRYPTED -eq 0 ]]; then
        # $ACTION is encrypt and file is not encrypted, encrypt it
        debug 3 "ACTION: $ACTION"
        debug 3 "ENCRYPTED: $ENCRYPTED"
        debug 0 "Encrypting:    $file"
        encrypt_file $file
    # If $ACTION is decrypt and file is encrypted, decrypt it
    elif [[ $ACTION == "decrypt" ]] && [[ $ENCRYPTED -eq 1 ]]; then
        # $ACTION is decrypt and file is encrypted, decrypt it
        debug 3 "ACTION: $ACTION"
        debug 3 "ENCRYPTED: $ENCRYPTED"
        debug 0 "Decrypting:    $file"
        decrypt_file $file
    # If $ACTION is encrypt and file is encrypted, skip it
    elif [[ $ACTION == "encrypt" ]] && [[ $ENCRYPTED -eq 1 ]]; then
        # $ACTION is encrypt and file is encrypted, skip it
        debug 3 "ACTION: $ACTION"
        debug 3 "ENCRYPTED: $ENCRYPTED"
        debug 0 "Skipping:      $file"
    # If $ACTION is decrypt and file is not encrypted, skip it
    elif [[ $ACTION == "decrypt" ]] && [[ $ENCRYPTED -eq 0 ]]; then
        # $ACTION is decrypt and file is not encrypted, skip it
        debug 3 "ACTION: $ACTION"
        debug 3 "ENCRYPTED: $ENCRYPTED"
        debug 0 "Skipping:      $file"
    else
        # $ACTION is not encrypt or decrypt, exit
        debug 2 "Invalid action"
    fi

done

echo "==============================================================================="
