"""
Entry point for Vercel deployment.
"""

import os
import sys
import importlib
import pkgutil
from dotenv import load_dotenv

# Fix imports for Vercel deployment
try:
    from fix_imports import fix_imports
    fix_imports()
    print("Fixed imports for Vercel deployment")
except Exception as e:
    print(f"Error fixing imports: {e}")

# Load environment variables from .env file if it exists (for local development)
load_dotenv()

# Set default environment variables if not provided
os.environ.setdefault("FC_SECRET_KEY", os.environ.get("FC_SECRET_KEY", os.urandom(24).hex()))

# Check for required environment variables
required_vars = ["MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET", "GROQ_API_KEY"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]

if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set these variables in your environment or .env file.")
    if not os.environ.get("VERCEL_ENV"):  # Only exit if not running on Vercel
        sys.exit(1)

# Debug information
print("Python version:", sys.version)
print("\nPython path:")
for path in sys.path:
    print(f"  - {path}")

print("\nDirectory structure:")
for root, dirs, files in os.walk('.'):
    level = root.replace('.', '').count(os.sep)
    indent = ' ' * 4 * level
    print(f"{indent}{os.path.basename(root)}/")
    sub_indent = ' ' * 4 * (level + 1)
    for f in files:
        if f.endswith('.py'):
            print(f"{sub_indent}{f}")

# Try to import the module directly
try:
    import function_cloud
    print("\nSuccessfully imported function_cloud")
    print(f"function_cloud path: {function_cloud.__path__ if hasattr(function_cloud, '__path__') else 'Not a package'}")

    # List submodules
    if hasattr(function_cloud, '__path__'):
        print("Submodules:")
        for _, name, ispkg in pkgutil.iter_modules(function_cloud.__path__, function_cloud.__name__ + '.'):
            print(f"  - {name} {'(package)' if ispkg else '(module)'}")
except ImportError as e:
    print(f"\nError importing function_cloud: {e}")

# Import the app after environment variables are set
try:
    # First try the direct import
    from function_cloud.web import get_app
    print("\nSuccessfully imported get_app from function_cloud.web")

    # Create the app
    app = get_app()
    print("Successfully created app")
except ImportError as e:
    print(f"\nError importing get_app from function_cloud.web: {e}")

    try:
        # Try the nested import as a fallback
        from function_cloud.function_cloud.web import get_app
        print("\nSuccessfully imported get_app from function_cloud.function_cloud.web")

        # Create the app
        app = get_app()
        print("Successfully created app")
    except ImportError as e2:
        print(f"\nError importing get_app from function_cloud.function_cloud.web: {e2}")

        # Fallback to a simple Flask app for debugging
        from flask import Flask
        app = Flask(__name__)

        @app.route('/')
        def debug_info():
            return "<h1>Debug Info</h1><pre>" + "\n".join([
                f"Python version: {sys.version}",
                f"Python path: {sys.path}",
                f"Current directory: {os.getcwd()}",
                f"Directory contents: {os.listdir('.')}",
                f"Error importing function_cloud.web: {e}",
                f"Error importing function_cloud.function_cloud.web: {e2}"
            ]) + "</pre>"

# This is used by Vercel - the WSGI app should be directly exposed
# Vercel will look for a variable named 'app' that is a WSGI application

# For local development
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
