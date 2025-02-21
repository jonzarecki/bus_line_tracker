#!/bin/bash

# Repository URL
REPO_URL="https://github.com/jonzarecki/bus_line_tracker.git"
TARGET_DIR="bus_line_tracking"

# Create and enter the target directory
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

# Initialize git and set up sparse checkout
git init
git remote add origin "$REPO_URL"
git config core.sparseCheckout true

# Specify the directory we want to clone
echo "custom_components/bus_line_tracker/" > .git/info/sparse-checkout

# Pull the files
git pull origin main

# Move files up one directory and clean up
mv custom_components/bus_line_tracker/* .
rm -rf custom_components
rm -rf .git

echo "Successfully cloned bus_line_tracker to $TARGET_DIR/" 