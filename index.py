"""
Entry point for Vercel deployment.
"""

import os
import sys
import importlib
import pkgutil
import shutil
from dotenv import load_dotenv

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Fix the import issue by creating a symlink or copying files
function_cloud_dir = os.path.join(current_dir, 'function_cloud')
nested_function_cloud_dir = os.path.join(function_cloud_dir, 'function_cloud')

# Create the nested function_cloud directory if it doesn't exist
if not os.path.exists(nested_function_cloud_dir):
    os.makedirs(nested_function_cloud_dir, exist_ok=True)
    print(f"Created directory: {nested_function_cloud_dir}")

    # Copy auth.py to the nested directory
    auth_source = os.path.join(function_cloud_dir, 'auth', 'auth.py')
    auth_dest = os.path.join(nested_function_cloud_dir, 'auth.py')
    if os.path.exists(auth_source):
        shutil.copy2(auth_source, auth_dest)
        print(f"Copied {auth_source} to {auth_dest}")

    # Create __init__.py in the nested directory
    with open(os.path.join(nested_function_cloud_dir, '__init__.py'), 'w') as f:
        f.write("""
# This file redirects imports from function_cloud.function_cloud to function_cloud
import sys
import importlib
from pathlib import Path

# Get the parent directory
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import all modules from the parent function_cloud package
import function_cloud

# Make all attributes of the parent package available in this package
for attr in dir(function_cloud):
    if not attr.startswith('__'):
        globals()[attr] = getattr(function_cloud, attr)
""")
    print(f"Created __init__.py in {nested_function_cloud_dir}")

# Load environment variables from .env file if it exists (for local development)
load_dotenv()

# Set default environment variables if not provided
os.environ.setdefault("FC_SECRET_KEY", os.environ.get("FC_SECRET_KEY", os.urandom(24).hex()))

# Check for required environment variables
required_vars = ["MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET", "GROQ_API_KEY"]
missing_vars = [var for var in required_vars if not os.environ.get(var)]

if missing_vars:
    print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
    print("These will be needed for full functionality.")

# Debug information
print("Python version:", sys.version)
print("\nPython path:")
for path in sys.path:
    print(f"  - {path}")

print("\nDirectory structure after fixes:")
for root, dirs, files in os.walk('.', topdown=True):
    level = root.replace('.', '').count(os.sep)
    indent = ' ' * 4 * level
    print(f"{indent}{os.path.basename(root) or '.'}/")
    sub_indent = ' ' * 4 * (level + 1)
    for f in sorted(files):
        if f.endswith('.py'):
            print(f"{sub_indent}{f}")

# Monkey patch the import system to handle the nested import
class CustomFinder:
    def find_spec(self, fullname, path, target=None):
        if fullname == 'function_cloud.function_cloud.auth':
            # Redirect to function_cloud.auth.auth
            spec = importlib.util.find_spec('function_cloud.auth.auth')
            return spec
        return None

sys.meta_path.insert(0, CustomFinder())

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
