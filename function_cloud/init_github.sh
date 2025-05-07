#!/bin/bash

# Initialize Git repository
git init

# Copy GitHub README
cp README-GITHUB.md README.md

# Add all files
git add .

# Initial commit
git commit -m "Initial commit"

# Instructions for GitHub
echo "Repository initialized. Now run:"
echo "1. Create a new repository on GitHub"
echo "2. Run the following commands:"
echo "   git remote add origin https://github.com/yourusername/function-cloud.git"
echo "   git branch -M main"
echo "   git push -u origin main"
