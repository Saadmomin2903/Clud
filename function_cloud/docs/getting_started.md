# Getting Started with Function Cloud

Function Cloud (FC) is a Python library that allows you to easily deploy functions to Modal.com's cloud infrastructure.

## Installation

```bash
pip install function-cloud
```

For LLM-powered dependency analysis:

```bash
pip install function-cloud[llm]
```

## Basic Usage

### 1. Import and Configure

```python
from function_cloud import FC

# Configure with your Modal token
FC.configure(token="your_modal_token")
```

### 2. Decorate Your Functions

```python
@FC.function
def add(x, y):
    return x + y
```

### 3. Use Your Functions

```python
# Call it locally
result = add(5, 10)
print(f"Result: {result}")  # Result: 15

# Get the cloud URL
url = add.get_url()
print(f"Function URL: {url}")

# Call it via HTTP
import requests
response = requests.post(url, json={"x": 5, "y": 10})
print(f"Remote result: {response.json()['result']}")  # Remote result: 15
```

## Advanced Configuration

```python
FC.configure(
    token="your_modal_token",
    region="us-east",
    memory=1024,
    timeout=30,
    cpu=1,
    llm_enabled=True,
    llm_api_key="your_groq_api_key",
    llm_provider="groq"
)
```

## Function Types

### Regular Functions

```python
@FC.function
def process_data(data):
    return data.upper()
```

### Class Methods

```python
class DataService:
    def __init__(self):
        self.counter = 0
        
    @FC.method
    def increment(self, amount=1):
        self.counter += amount
        return self.counter
```

### API Endpoints

```python
@FC.endpoint(methods=["GET", "POST"])
def api_handler(name=None, action=None):
    if action == "greet":
        return {"message": f"Hello, {name}!"}
    return {"error": "Invalid action"}
```

## Dependency Management

FC automatically analyzes your function's dependencies and creates the appropriate container environment. For more complex dependencies, it can use Groq LLM to enhance the analysis.

```python
# Enable LLM-powered dependency analysis
FC.configure(
    token="your_modal_token",
    llm_enabled=True,
    llm_api_key="your_groq_api_key"
)
```
