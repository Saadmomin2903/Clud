"""
Test script to verify that the Function Cloud (FC) library works with default credentials.
"""

from function_cloud import FC
from function_cloud.config import FCConfig

print("Function Cloud (FC) library is installed correctly!")

# Configure FC with default credentials
FC.configure()

print(f"Using Modal token: {FCConfig.token}")
print(f"Using Groq API key: {FCConfig.llm_api_key}")

# Define a simple function
@FC.function
def add(x, y):
    return x + y

# Call the function locally
result = add(5, 10)
print(f"Result of add(5, 10): {result}")

# Get the URL
url = add.get_url()
print(f"Function URL: {url}")

print("Test completed successfully!")
