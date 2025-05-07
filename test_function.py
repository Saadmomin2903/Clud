#!/usr/bin/env python3
"""
Test script to call the deployed function.
"""

import os
import requests
import json

# The URL of the deployed function
FUNCTION_URL = "https://fc_app--modal-functions-function-86060930.modal.run"

def test_function():
    """Test the deployed function with different inputs."""
    # Test case 1: a=42, b=58
    payload = {"a": 42, "b": 58}
    print(f"Testing with payload: {payload}")
    
    try:
        # Make the request
        response = requests.post(FUNCTION_URL, json=payload)
        
        # Print the response
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Try to parse the JSON response
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Parsed result: {result}")
            except json.JSONDecodeError:
                print("Response is not valid JSON")
    except Exception as e:
        print(f"Error making request: {e}")
    
    print("\n" + "-"*50 + "\n")
    
    # Test case 2: a=100, b=200
    payload = {"a": 100, "b": 200}
    print(f"Testing with payload: {payload}")
    
    try:
        # Make the request with additional headers
        headers = {
            "Content-Type": "application/json",
            "Host": "fc_app--modal-functions-function-86060930.modal.run"
        }
        response = requests.post(FUNCTION_URL, json=payload, headers=headers)
        
        # Print the response
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Try to parse the JSON response
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Parsed result: {result}")
            except json.JSONDecodeError:
                print("Response is not valid JSON")
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    test_function()
