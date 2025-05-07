"""
Simple test script for the Function Cloud (FC) library.
"""

from function_cloud import FC

print("Function Cloud (FC) library is installed correctly!")

# Configure FC
FC.configure(token="test_token")

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
