# Function Cloud

A Python library for easily deploying functions to Modal.com's cloud infrastructure.

## Features

- **Simple Function Wrapping**: Deploy any Python function to the cloud with a simple decorator syntax
- **Automatic URL Generation**: Each deployed function gets a unique endpoint URL
- **Support for Multiple Function Types**: Synchronous functions, asynchronous functions, class methods, API endpoints
- **Token-based Authentication**: Secure deployment and function calls
- **Intelligent Dependency Management**: LLM-powered analysis of function dependencies
- **Environment Configuration**: Automatic container setup for function execution
- **Web Interface**: User-friendly dashboard for managing functions
- **Google OAuth Integration**: Secure authentication with Google accounts
- **Token Management**: Generate, refresh, and revoke tokens

## Installation

```bash
pip install function-cloud
```

For additional features:

```bash
# For LLM-powered dependency analysis
pip install function-cloud[llm]

# For authentication features
pip install function-cloud[auth]

# For web interface
pip install function-cloud[web]

# For all features
pip install function-cloud[all]
```

## Quick Start

```python
from function_cloud import FC

# Use the built-in default credentials
FC.configure()

# Decorate your function
@FC.function
def add(x, y):
    return x + y

# Call it locally
result = add(5, 10)
print(f"Result: {result}")  # Result: 15

# Get the cloud URL
url = add.get_url()
print(f"Function URL: {url}")
```

## Web Interface

Function Cloud comes with a web interface for managing your functions and tokens.

### Running the Web Interface

```bash
# Install web dependencies
pip install function-cloud[web]

# Run the web interface
function-cloud web
```

## Deployment

This repository includes configuration for deploying the web interface to Vercel.

### Vercel Deployment

1. Fork this repository
2. Connect your Vercel account to your GitHub repository
3. Configure the following environment variables in Vercel:
   - `FC_GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `FC_GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
   - `FC_SECRET_KEY`: A random secret key for Flask sessions

### Google OAuth Configuration

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Select "Web application" as the application type
6. Add authorized redirect URIs:
   - For local development: `http://localhost:5000/callback`
   - For Vercel deployment: `https://your-vercel-app.vercel.app/callback`

## License

MIT
