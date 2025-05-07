#!/usr/bin/env python3
"""
Test the add function locally.
"""

from function_cloud import FC
import os
import sys
from dotenv import load_dotenv
from function_cloud.config import FCConfig

# Load environment variables from .env file
load_dotenv()

# Check for required environment variables
if not os.environ.get("MODAL_TOKEN_ID") or not os.environ.get("MODAL_TOKEN_SECRET"):
    print("Error: MODAL_TOKEN_ID and MODAL_TOKEN_SECRET environment variables are required.")
    print("Please set them in your .env file or environment variables.")
    sys.exit(1)

if not os.environ.get("GROQ_API_KEY"):
    print("Error: GROQ_API_KEY environment variable is not set.")
    print("Please set it in your .env file or environment variables.")
    sys.exit(1)

# Configure FC with environment variables
FC.configure()

@FC.function
def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b

def test_function():
    """Test the function with different inputs."""
    # Test case 1
    a, b = 42, 58
    result = add(a, b)
    print(f"add({a}, {b}) = {result}")

    # Test case 2
    a, b = 100, 200
    result = add(a, b)
    print(f"add({a}, {b}) = {result}")

    # Get the function URL
    url = add.get_url()
    print(f"Function URL: {url}")
    print("Note: This is a mock URL for demonstration purposes.")

if __name__ == "__main__":
    test_function()
