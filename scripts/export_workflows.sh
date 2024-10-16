#!/bin/bash

# Function to print usage
print_usage() {
    echo "Usage: $0 [--dir <directory>]... [--file <file>]... [--ignore <pattern>]... [--output <output_file>]"
    echo "  --dir <directory>    Directory to recursively process"
    echo "  --file <file>        Specific file to include"
    echo "  --ignore <pattern>   Pattern to ignore (can be used multiple times)"
    echo "  --output <file>      Output file (default: workflows_YYYYMMDDHHMMSS.txt in the root directory)"
}

# Initialize arrays
dirs=()
files=()
ignore_patterns=()

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dir)
            dirs+=("$2")
            shift 2
            ;;
        --file)
            # Use eval to properly handle wildcard patterns
            eval "files+=($(printf '%q' "$2"))"
            shift 2
            ;;
        --ignore)
            ignore_patterns+=("$2")
            shift 2
            ;;
        --output)
            output_file="$2"
            shift 2
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Read .gitignore patterns
gitignore_file="$(git rev-parse --show-toplevel)/.gitignore"
gitignore_patterns=($(read_gitignore "$gitignore_file"))
ignore_patterns+=("${gitignore_patterns[@]}")

# Set default output file if not specified
if [ -z "$output_file" ]; then
    # Get current date and time in YYYYMMDDHHMMSS format
    current_datetime=$(date +"%Y%m%d%H%M%S")
    # Get current git repository root directory
    root_directory=$(git rev-parse --show-toplevel)
    output_file="${root_directory}/data/workflows_${current_datetime}.txt"
fi

# Function to read .gitignore and convert patterns to an array
read_gitignore() {
    local gitignore_file="$1"
    local patterns=()
    if [ -f "$gitignore_file" ]; then
        while IFS= read -r line || [[ -n "$line" ]]; do
            # Ignore empty lines and comments
            if [[ -n "$line" && ! "$line" =~ ^\s*# ]]; then
                patterns+=("$line")
            fi
        done < "$gitignore_file"
    fi
    echo "${patterns[@]}"
}

# Function to check if a file should be ignored
should_ignore() {
    local file="$1"
    for pattern in "${ignore_patterns[@]}"; do
        if [[ "$file" == *"$pattern"* ]] || git check-ignore -q "$file"; then
            return 0
        fi
    done
    return 1
}

# Function to process a directory
process_directory() {
    local dir="$1"
    echo "# Tree structure of $dir" >> "$output_file"
    tree "$dir" >> "$output_file"
    echo "" >> "$output_file"

    while IFS= read -r -d '' file; do
        if [ -f "$file" ] && ! should_ignore "$file"; then
            echo "# $file" >> "$output_file"
            cat "$file" >> "$output_file"
            echo "" >> "$output_file"
        fi
    done < <(find "$dir" -type f -print0)
}

# Process directories
for dir_pattern in "${dirs[@]}"; do
    for dir in $dir_pattern; do
        if [ -d "$dir" ]; then
            process_directory "$dir"
        else
            echo "Warning: Directory not found - $dir"
        fi
    done
done

# Process individual files
for file_pattern in "${files[@]}"; do
    for file in $file_pattern; do
        if [ -f "$file" ] && ! should_ignore "$file"; then
            echo "# $file" >> "$output_file"
            cat "$file" >> "$output_file"
            echo "" >> "$output_file"
        else
            echo "Warning: File not found or ignored - $file"
        fi
    done
done

echo "Generated $output_file"
