# Function Cloud Production Guide

This comprehensive guide will help you take Function Cloud from development to production with best practices for deployment, monitoring, and scaling.

## Table of Contents

- [Setup and Installation](#setup-and-installation)
- [Configuration Management](#configuration-management)
- [Function Development](#function-development)
- [Deployment Strategies](#deployment-strategies)
- [Testing and Validation](#testing-and-validation)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Best Practices](#security-best-practices)
- [Scaling Considerations](#scaling-considerations)
- [Cost Optimization](#cost-optimization)
- [Troubleshooting](#troubleshooting)

## Setup and Installation

### Prerequisites

- Python 3.8+ installed
- Modal.com account with API credentials
- Groq API key (for LLM-powered dependency analysis)
- Git for version control

### Installation

```bash
# Create a dedicated project directory
mkdir my_fc_project && cd my_fc_project

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Function Cloud with all dependencies
pip install function-cloud[all]

# Create requirements.txt for reproducibility
pip freeze > requirements.txt
```

## Configuration Management

### Environment Variables

For development:

```bash
# Copy the example .env file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use your preferred editor

# Load environment variables
source .env  # On Windows, use a tool like direnv
```

For production with Vercel:

1. Add your environment variables in the Vercel dashboard:
   - Go to your project settings
   - Navigate to the "Environment Variables" tab
   - Add each variable from your .env file

For production with other platforms:

- Set these in your CI/CD pipeline or server environment
- Never commit actual credentials to your repository

### Configuration File

For local development, you can use a configuration file:

```bash
# Create config directory
mkdir -p ~/.function_cloud

# Create configuration file
cat > ~/.function_cloud/config.json << EOL
{
    "region": "us-east",
    "memory": 1024,
    "timeout": 120,
    "cpu": 1,
    "llm_enabled": true,
    "llm_provider": "groq",
    "stub_name": "my_app"
}
EOL
```

Note: Sensitive credentials should be stored as environment variables, not in the config file.

## Function Development

### Basic Function Structure

```python
# functions.py
from function_cloud import FC
import os

# Configure with credentials
FC.configure()

@FC.function
def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b

@FC.endpoint(methods=["GET", "POST"])
def api_handler(name: str = None, action: str = "greet") -> dict:
    """A simple API endpoint that greets users."""
    if action == "greet":
        return {"message": f"Hello, {name or 'World'}!"}
    return {"error": "Invalid action"}

@FC.function(dependencies=["pandas", "numpy", "matplotlib"])
def analyze_data(data_url: str) -> dict:
    """Analyze data from a URL."""
    import pandas as pd
    import numpy as np

    # Download and analyze data
    df = pd.read_csv(data_url)

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "mean": df.mean().to_dict(),
        "correlation": df.corr().to_dict()
    }
```

### Addressing Modal Deprecation Warnings

```python
# modern_deployment.py
from function_cloud import FC
import modal

# Configure Function Cloud
FC.configure()

# Custom deployment function that addresses deprecation warnings
def deploy_with_latest_modal(func, dependencies=None):
    """Deploy a function using the latest Modal recommendations."""
    if dependencies is None:
        dependencies = []

    # Create an App instead of a Stub
    app = modal.App(f"fc_app_{func.__name__}")

    # Create image with explicit local module inclusion
    image = modal.Image.debian_slim(python_version="3.10")

    # Add dependencies
    if dependencies:
        image = image.pip_install(dependencies)

    # Explicitly add local Python modules
    image = image.add_local_python_source("function_cloud")

    # Define the Modal function
    @app.function(image=image)
    def modal_func(*args, **kwargs):
        return func(*args, **kwargs)

    # Deploy and return URL
    app.deploy()
    return f"https://{app.name}--{modal_func.name}.modal.run"
```

## Deployment Strategies

### Deployment Script

```python
# deploy.py
#!/usr/bin/env python3
"""
Deployment script for Function Cloud functions.
"""

import os
import sys
import argparse
import json
from functions import add, api_handler, analyze_data

def deploy_function(func, test_args=None):
    """Deploy a single function."""
    try:
        # Call the function once to trigger deployment
        if test_args:
            if isinstance(test_args, dict):
                func(**test_args)
            else:
                func(*test_args)

        # Get the URL
        url = func.get_url()
        return url
    except Exception as e:
        print(f"Error deploying {func.__name__}: {str(e)}")
        return None

def save_urls(urls_dict, filename="function_urls.json"):
    """Save function URLs to a file."""
    with open(filename, "w") as f:
        json.dump(urls_dict, f, indent=2)
    print(f"URLs saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Deploy Function Cloud functions.")
    parser.add_argument("--function", help="Deploy a specific function")
    parser.add_argument("--all", action="store_true", help="Deploy all functions")
    parser.add_argument("--save", action="store_true", help="Save URLs to a file")

    args = parser.parse_args()

    functions = {
        "add": (add, (1, 2)),
        "api_handler": (api_handler, {"name": "Test"}),
        "analyze_data": (analyze_data, {"data_url": "https://raw.githubusercontent.com/datasets/iris/master/data/iris.csv"})
    }

    urls = {}

    if args.function:
        if args.function not in functions:
            print(f"Unknown function: {args.function}")
            return

        func, test_args = functions[args.function]
        url = deploy_function(func, test_args)
        if url:
            urls[args.function] = url
            print(f"{args.function} deployed at: {url}")

    elif args.all:
        for name, (func, test_args) in functions.items():
            print(f"Deploying {name}...")
            url = deploy_function(func, test_args)
            if url:
                urls[name] = url
                print(f"{name} deployed at: {url}")

    else:
        parser.print_help()
        return

    if args.save and urls:
        save_urls(urls)

if __name__ == "__main__":
    main()
```

### CI/CD Integration

#### GitHub Actions with Vercel Deployment

Create a GitHub Actions workflow file at `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install Vercel CLI
      run: npm install -g vercel

    - name: Deploy to Vercel
      run: |
        vercel --token ${{ secrets.VERCEL_TOKEN }} --prod --yes
      env:
        MODAL_TOKEN_ID: ${{ secrets.MODAL_TOKEN_ID }}
        MODAL_TOKEN_SECRET: ${{ secrets.MODAL_TOKEN_SECRET }}
        GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        FC_GOOGLE_CLIENT_ID: ${{ secrets.FC_GOOGLE_CLIENT_ID }}
        FC_GOOGLE_CLIENT_SECRET: ${{ secrets.FC_GOOGLE_CLIENT_SECRET }}
        FC_SECRET_KEY: ${{ secrets.FC_SECRET_KEY }}
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
```

#### Setting Up GitHub Secrets

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add the following secrets:
   - `VERCEL_TOKEN`: Your Vercel API token
   - `MODAL_TOKEN_ID`: Your Modal token ID
   - `MODAL_TOKEN_SECRET`: Your Modal token secret
   - `GROQ_API_KEY`: Your Groq API key
   - `FC_GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `FC_GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
   - `FC_SECRET_KEY`: A random secret key for Flask
   - `SUPABASE_URL`: Your Supabase URL (if using Supabase)
   - `SUPABASE_KEY`: Your Supabase key (if using Supabase)

#### Setting Up Vercel Environment Variables

1. Go to your Vercel project dashboard
2. Navigate to Settings > Environment Variables
3. Add all the same environment variables as in your GitHub secrets
4. Make sure to mark sensitive variables as "Encrypted"

## Testing and Validation

### Testing Script

```python
# test_functions.py
#!/usr/bin/env python3
"""
Test script for deployed functions.
"""

import requests
import json
import time
import argparse

def load_urls(filename="function_urls.json"):
    """Load function URLs from a file."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def test_add_function(url):
    """Test the add function."""
    print(f"Testing add function at {url}")

    test_cases = [
        {"a": 5, "b": 10, "expected": 15},
        {"a": 42, "b": 58, "expected": 100},
        {"a": -5, "b": 5, "expected": 0}
    ]

    for i, test in enumerate(test_cases):
        try:
            response = requests.post(url, json={"a": test["a"], "b": test["b"]})

            print(f"Test {i+1}: {test['a']} + {test['b']}")
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                if result.get("result") == test["expected"]:
                    print(f"  ✅ PASS: Got expected result {test['expected']}")
                else:
                    print(f"  ❌ FAIL: Expected {test['expected']}, got {result.get('result')}")
            else:
                print(f"  ❌ FAIL: Request failed with status {response.status_code}")
        except Exception as e:
            print(f"  ❌ FAIL: Error making request: {e}")

        print()
        time.sleep(1)  # Avoid rate limiting

def main():
    parser = argparse.ArgumentParser(description="Test deployed functions.")
    parser.add_argument("--function", choices=["add", "api_handler", "analyze_data"], help="Test a specific function")
    parser.add_argument("--url", help="Specify a custom URL for testing")
    parser.add_argument("--urls-file", default="function_urls.json", help="JSON file containing function URLs")

    args = parser.parse_args()

    if args.url:
        if not args.function:
            print("Error: When specifying a URL, you must also specify the function type with --function")
            return

        if args.function == "add":
            test_add_function(args.url)
        # Add other function tests as needed

    else:
        urls = load_urls(args.urls_file)
        if not urls:
            print(f"Error: No URLs found in {args.urls_file}")
            return

        if args.function:
            if args.function not in urls:
                print(f"Error: URL for {args.function} not found in {args.urls_file}")
                return

            if args.function == "add":
                test_add_function(urls[args.function])
            # Add other function tests as needed

        else:
            if "add" in urls:
                test_add_function(urls["add"])
                print("\n" + "="*50 + "\n")
            # Add other function tests as needed

if __name__ == "__main__":
    main()
```

## Monitoring and Logging

### Basic Monitoring Script

```python
# monitor.py
#!/usr/bin/env python3
"""
Monitoring script for Function Cloud deployed functions.
"""

import requests
import time
import datetime
import json
import os
from typing import Dict, Any

def check_function(name: str, url: str, payload: Dict[str, Any]) -> bool:
    """Check if a function is working."""
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

def monitor_functions(urls_file="function_urls.json", interval=300):
    """Monitor functions at regular intervals."""
    # Load function URLs
    with open(urls_file, "r") as f:
        urls = json.load(f)

    # Test payloads for each function
    payloads = {
        "add": {"a": 1, "b": 2},
        "api_handler": {"name": "Monitor"},
        "analyze_data": {"data_url": "https://raw.githubusercontent.com/datasets/iris/master/data/iris.csv"}
    }

    while True:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n=== Function Status Check: {timestamp} ===")

        for name, url in urls.items():
            if name in payloads:
                status = check_function(name, url, payloads[name])
                status_str = "✅ OK" if status else "❌ FAIL"
                print(f"{name}: {status_str}")

        print(f"Next check in {interval} seconds...")
        time.sleep(interval)

if __name__ == "__main__":
    monitor_functions()
```

## Security Best Practices

1. **Credential Management**
   - Never hardcode credentials in your code
   - Use environment variables or secure credential storage
   - Rotate credentials regularly

2. **Input Validation**
   - Always validate and sanitize inputs
   - Use type hints and validation libraries

3. **Dependency Management**
   - Regularly update dependencies
   - Use dependency scanning tools
   - Pin dependency versions

4. **Access Control**
   - Implement proper authentication for sensitive functions
   - Use API keys or OAuth tokens
   - Implement rate limiting

## Scaling Considerations

1. **Function Design**
   - Keep functions small and focused
   - Optimize for cold start times
   - Use appropriate memory and CPU settings

2. **Caching**
   - Implement caching for expensive operations
   - Use Redis or Memcached for shared caching

3. **Asynchronous Processing**
   - Use queues for long-running tasks
   - Implement webhooks for callbacks

## Cost Optimization

1. **Resource Allocation**
   - Right-size memory and CPU for functions
   - Use timeout settings appropriately

2. **Batching**
   - Batch operations when possible
   - Implement bulk processing

3. **Monitoring**
   - Track usage and costs
   - Set up alerts for unusual activity

## Troubleshooting

### Common Issues

1. **Deployment Failures**
   - Check credentials
   - Verify dependencies
   - Check for syntax errors

2. **Runtime Errors**
   - Check logs
   - Test locally first
   - Verify input formats

3. **Performance Issues**
   - Check memory and CPU settings
   - Look for inefficient code
   - Consider caching

### Debugging Tools

```python
# debug.py
from function_cloud import FC
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Enable debug mode
FC.configure(debug=True)

# Create a debug wrapper
def debug_function(func):
    def wrapper(*args, **kwargs):
        logging.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logging.debug(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

# Example usage
@FC.function
@debug_function
def add(a: int, b: int) -> int:
    return a + b
```

---

This guide covers the essential aspects of using Function Cloud in a production environment. For more detailed information, refer to the official documentation or contact support.
