"""
Function Cloud (FC) Library
===========================

A Python library for easily deploying functions to Modal.com's cloud infrastructure.

Usage:
------
```python
from function_cloud import FC

# Configure with your Modal token
FC.configure(token="your_modal_token")

# Decorate your function
@FC.function
def my_function(x, y):
    return x + y

# Call it locally
result = my_function(5, 10)

# Get the cloud URL
url = my_function.get_url()
```

For more examples, see the documentation.
"""

from function_cloud.core import FC
from function_cloud.auth import FCAuth

__version__ = "0.1.0"
