"""
Basic example of using Function Cloud (FC).
"""

from function_cloud import FC

# Configure with your Modal token
FC.configure(token="your_modal_token")

# Simple function example
@FC.function
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Use it locally first
result = calculate_fibonacci(10)
print(f"Fibonacci(10) = {result}")

# Get the cloud URL
url = calculate_fibonacci.get_url()
print(f"Function URL: {url}")

# Call it via HTTP (uncomment to use)
# import requests
# response = requests.get(url, params={"n": 10})
# print(f"Remote result: {response.json()['result']}")
