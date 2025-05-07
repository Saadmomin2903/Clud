"""
Test script to verify that the Function Cloud (FC) library is installed correctly.
"""

from function_cloud import FC
from function_cloud.config import FCConfig

print("Function Cloud (FC) library is installed correctly!")
print(f"Version: {FC.__version__ if hasattr(FC, '__version__') else 'Unknown'}")

# Configure FC
FC.configure(token="test_token")

# Define a simple function
@FC.function
def add(x, y):
    return x + y

# Mock the deployment to avoid Modal dependency
# This is just for testing the installation
add._fc_deployed = True
add._fc_url = "https://example.com/function"

# Call the function locally
result = add(5, 10)
print(f"Result of add(5, 10): {result}")

# Get the URL
url = add.get_url()
print(f"Function URL: {url}")

print("Test completed successfully!")
