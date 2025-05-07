"""
Fix imports for Vercel deployment.
"""

import os
import sys
import importlib.util

def fix_imports():
    """
    Fix imports for Vercel deployment by ensuring the correct module structure.
    """
    # Add the current directory to the Python path if not already there
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Check if function_cloud.auth exists
    auth_init_path = os.path.join(current_dir, 'function_cloud', 'auth', '__init__.py')
    if os.path.exists(auth_init_path):
        # Check the content of the file
        with open(auth_init_path, 'r') as f:
            content = f.read()
        
        # If the file contains an incorrect import, fix it
        if 'from function_cloud.function_cloud.auth import FCAuth' in content:
            fixed_content = content.replace(
                'from function_cloud.function_cloud.auth import FCAuth',
                'from function_cloud.auth.auth import FCAuth'
            )
            with open(auth_init_path, 'w') as f:
                f.write(fixed_content)
            print(f"Fixed import in {auth_init_path}")
    
    # Create a symlink if needed to handle nested imports
    function_cloud_dir = os.path.join(current_dir, 'function_cloud')
    nested_function_cloud_dir = os.path.join(function_cloud_dir, 'function_cloud')
    
    if os.path.exists(function_cloud_dir) and not os.path.exists(nested_function_cloud_dir):
        try:
            # Create a symlink to handle nested imports
            os.symlink(function_cloud_dir, nested_function_cloud_dir)
            print(f"Created symlink from {function_cloud_dir} to {nested_function_cloud_dir}")
        except OSError as e:
            print(f"Error creating symlink: {e}")
            
            # If symlink creation fails, create a simple __init__.py file
            os.makedirs(nested_function_cloud_dir, exist_ok=True)
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

# Import specific modules that might be needed
try:
    from function_cloud.auth.auth import FCAuth
    globals()['auth'] = FCAuth
except ImportError:
    pass
""")
            print(f"Created __init__.py in {nested_function_cloud_dir}")
            
            # Create auth.py in the nested directory
            with open(os.path.join(nested_function_cloud_dir, 'auth.py'), 'w') as f:
                f.write("""
# This file redirects imports from function_cloud.function_cloud.auth to function_cloud.auth
from function_cloud.auth.auth import FCAuth
""")
            print(f"Created auth.py in {nested_function_cloud_dir}")

if __name__ == "__main__":
    fix_imports()
