#!/bin/bash
# Script to create a GitHub repository and connect it to the local repository

REPO_NAME="Scheduling"
GITHUB_USERNAME=""  # Replace with your GitHub username
GITHUB_TOKEN=""     # Replace with your GitHub personal access token (optional if using gh CLI)

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo "Using GitHub CLI to create repository..."
    gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
    echo "Repository created and connected!"
    exit 0
fi

# If GitHub CLI is not available, use GitHub API
if [ -z "$GITHUB_USERNAME" ]; then
    echo "Error: Please set GITHUB_USERNAME in this script"
    echo "Or install GitHub CLI: https://cli.github.com/"
    exit 1
fi

# Create repository using GitHub API
echo "Creating repository using GitHub API..."
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Warning: GITHUB_TOKEN not set. You may need to authenticate."
    echo "Creating repository (may require authentication)..."
    curl -X POST \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d "{\"name\":\"$REPO_NAME\",\"private\":false}"
else
    curl -X POST \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/user/repos \
        -d "{\"name\":\"$REPO_NAME\",\"private\":false}"
fi

# Add remote and push
echo "Connecting to remote repository..."
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
git branch -M main 2>/dev/null || git branch -M master
git push -u origin main 2>/dev/null || git push -u origin master

echo "Done! Repository created at: https://github.com/$GITHUB_USERNAME/$REPO_NAME"

