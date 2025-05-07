#!/usr/bin/env python3
"""
Test script to verify the Groq API key.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Groq API key from environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY environment variable is not set.")
    print("Please set it in your .env file or environment variables.")
    sys.exit(1)

print(f"Testing Groq API key: {GROQ_API_KEY[:10]}...")

try:
    import groq
    print("Groq package is installed")
except ImportError:
    print("Groq package is not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
    import groq
    print("Groq package installed successfully")

try:
    # Create a Groq client
    client = groq.Client(api_key=GROQ_API_KEY)
    print("Groq client created successfully")

    # Test the API key with a simple request
    print("Sending test request to Groq API...")
    response = client.chat.completions.create(
        model="llama3-8b-8192",  # Using a smaller model for testing
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        max_tokens=10
    )

    print(f"Groq API test successful! Response: {response.choices[0].message.content}")
    print("API key is valid and working correctly")
except Exception as e:
    print(f"Error testing Groq API: {e}")
    import traceback
    print(f"Detailed error: {traceback.format_exc()}")
    print("API key may be invalid or there may be other issues")

print("Test completed")
