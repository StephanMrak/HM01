#!/bin/bash

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found in the current directory."
    exit 1
fi

# Ensure sudo privileges are available
if ! command -v sudo >/dev/null 2>&1; then
    echo "Error: sudo is required but not installed."
    exit 1
fi

# Update apt package index
echo "Updating apt package index..."
sudo apt update

# Read requirements.txt line by line
while IFS= read -r line; do
    # Skip empty lines or comments
    if [[ -z "$line" || "$line" =~ ^# ]]; then
        continue
    fi

    # Extract package name (handle formats like "package==version" or "package>=version")
    package=$(echo "$line" | sed -E 's/[<>=!].*//')
    package=$(echo "$package" | tr '[:upper:]' '[:lower:]' | tr '-' '_')

    if [ -z "$package" ]; then
        echo "Skipping invalid line: $line"
        continue
    fi

    echo "Attempting to install $package..."

    # Try installing with apt-get
    echo "Trying apt-get: python3-$package"
    if sudo apt install -y "python3-$package" 2>/dev/null; then
        echo "Successfully installed python3-$package via apt-get"
    else
        echo "apt-get failed for python3-$package, falling back to pip3"
        # Try installing with pip3
        if sudo pip3 install "$line"; then
            echo "Successfully installed $line via pip3"
        else
            echo "Error: Failed to install $line via pip3"
        fi
    fi
done < requirements.txt

echo "Installation process completed."
