import os
import json
import re

# Define paths
DOCS_DIR = "/data/docs"
OUTPUT_FILE = "/data/docs/index.json"

def extract_h1_title(file_path):
    """Extracts the first H1 title (# Title) from a Markdown file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                match = re.match(r"^# (.+)", line.strip())  # Look for first # Title
                if match:
                    return match.group(1)  # Return the extracted title
        return None  # No H1 title found
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def create_index():
    """Finds all Markdown files in /data/docs and creates an index.json file."""
    index = {}

    if not os.path.exists(DOCS_DIR):
        print(f"Error: Directory {DOCS_DIR} does not exist.")
        return

    # Walk through all Markdown files in /data/docs/
    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):  # Only process .md files
                file_path = os.path.join(root, file)
                title = extract_h1_title(file_path) or "Untitled"
                relative_path = os.path.relpath(file_path, DOCS_DIR)  # Remove /data/docs/ prefix
                index[relative_path] = title

    # Write index.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as json_file:
        json.dump(index, json_file, indent=4)

    print(f"Index file created at {OUTPUT_FILE}")

# Run the function
create_index()
