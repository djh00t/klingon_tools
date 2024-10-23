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
            shift
            while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
                for dir in $1; do
                    dirs+=("$dir")
                done
                shift
            done
            ;;
        --file)
            shift
            while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
                for file in $1; do
                    files+=("$file")
                done
                shift
            done
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

# Set default output file if not specified
if [ -z "$output_file" ]; then
    # Get current date and time in YYYYMMDDHHMMSS format
    current_datetime=$(date +"%Y%m%d%H%M%S")
    # Get current git repository root directory
    root_directory=$(git rev-parse --show-toplevel)
    output_dir="${root_directory}/data"
    mkdir -p "$output_dir"
    output_file="${output_dir}/workflows_${current_datetime}.txt"
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

# Read .gitignore patterns
gitignore_file="$(git rev-parse --show-toplevel)/.gitignore"
gitignore_patterns=($(read_gitignore "$gitignore_file"))
ignore_patterns+=("${gitignore_patterns[@]}")

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
    
    # Create a temporary file to store additional files for tree
    temp_file=$(mktemp)
    
    # Add individual files to the temporary file
    for file in "${files[@]}"; do
        if [ -f "$file" ] && ! should_ignore "$file"; then
            echo "$file" >> "$temp_file"
        fi
    done
    
    # Use tree with the additional files
    if [ -s "$temp_file" ]; then
        tree "$dir" $(cat "$temp_file") >> "$output_file"
    else
        tree "$dir" >> "$output_file"
    fi
    
    # Remove the temporary file
    rm "$temp_file"
    
    echo "" >> "$output_file"

    # Process files in the directory
    while IFS= read -r -d '' file; do
        if [ -f "$file" ] && ! should_ignore "$file"; then
            echo "# $file" >> "$output_file"
            cat "$file" >> "$output_file"
            echo "" >> "$output_file"
        fi
    done < <(find "$dir" -type f -print0)
    
    # Process individual files
    for file in "${files[@]}"; do
        if [ -f "$file" ] && ! should_ignore "$file" && [[ ! "$file" == "$dir"* ]]; then
            echo "# $file" >> "$output_file"
            cat "$file" >> "$output_file"
            echo "" >> "$output_file"
        fi
    done
}


# Print git repo information
repo_name=$(basename -s .git `git config --get remote.origin.url`)
repo_dir=$(git rev-parse --show-toplevel)
repo_origin=$(git config --get remote.origin.url)
echo "Git Repository: $repo_name"
echo "Repository Directory: $repo_dir"
echo "Repository Origin: $repo_origin"
echo ""

# Initialize counters
total_files=0
total_lines=0

# Process directories
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        process_directory "$dir"
    else
        echo "Warning: Directory not found - $dir"
    fi
done

# Count total files and lines
total_files=$(grep -c '^# ' "$output_file")
total_lines=$(wc -l < "$output_file")

# Get file size in bytes
file_size_bytes=$(wc -c < "$output_file")
file_size_mb=$(bc <<< "scale=2; $file_size_bytes / 1048576")
file_size_gb=$(bc <<< "scale=2; $file_size_bytes / 1073741824")

echo "Generated $output_file"
echo "Tree structure:"
tree "${dirs[@]}"
echo "Total files included: $total_files"
echo "Total lines in output: $total_lines"
echo "Output file size: $file_size_bytes bytes ($file_size_mb MB / $file_size_gb GB)"
