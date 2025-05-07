#!/bin/bash

# Clean up previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python setup.py sdist bdist_wheel

# Check the package
twine check dist/*

echo "Package built successfully. To upload to PyPI, run:"
echo "twine upload dist/*"
