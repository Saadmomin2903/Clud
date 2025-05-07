"""
Debug script to print Python path and module structure.
"""

import os
import sys
import importlib
import pkgutil

def print_module_structure(package_name):
    """Print the structure of a module."""
    try:
        package = importlib.import_module(package_name)
        print(f"Package: {package_name}")
        print(f"Package path: {package.__path__ if hasattr(package, '__path__') else 'Not a package'}")
        
        if hasattr(package, '__path__'):
            print("Submodules:")
            for _, name, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
                print(f"  - {name} {'(package)' if ispkg else '(module)'}")
    except ImportError as e:
        print(f"Error importing {package_name}: {e}")

def main():
    """Main function."""
    print("Python version:", sys.version)
    print("\nPython path:")
    for path in sys.path:
        print(f"  - {path}")
    
    print("\nEnvironment variables:")
    for key, value in os.environ.items():
        if key.startswith("FC_") or key in ["MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET", "GROQ_API_KEY", "VERCEL_ENV"]:
            print(f"  - {key}: {'*' * len(value)}")  # Don't print actual values for security
    
    print("\nModule structure:")
    print_module_structure('function_cloud')
    
    try:
        from function_cloud.auth import FCAuth
        print("\nSuccessfully imported FCAuth from function_cloud.auth")
    except ImportError as e:
        print(f"\nError importing FCAuth from function_cloud.auth: {e}")
    
    try:
        from function_cloud.web import get_app
        print("\nSuccessfully imported get_app from function_cloud.web")
    except ImportError as e:
        print(f"\nError importing get_app from function_cloud.web: {e}")

if __name__ == "__main__":
    main()
