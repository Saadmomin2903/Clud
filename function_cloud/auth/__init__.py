"""
Authentication module for Function Cloud (FC).
"""

# Try both import paths to handle different deployment environments
try:
    # First try the direct import
    from function_cloud.auth.auth import FCAuth
except ImportError:
    try:
        # Then try the nested import
        from function_cloud.function_cloud.auth import FCAuth
    except ImportError:
        # If both fail, define a placeholder class that will raise a more helpful error
        class FCAuth:
            def __init__(self, *args, **kwargs):
                raise ImportError(
                    "Could not import FCAuth. This might be due to a deployment issue. "
                    "Please check that the function_cloud package is installed correctly."
                )

__all__ = ["FCAuth"]
