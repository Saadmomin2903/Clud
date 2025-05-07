"""
Web interface for Function Cloud (FC).
"""

# Try both import paths to handle different deployment environments
try:
    # First try the direct import
    from function_cloud.web.app import create_app
except ImportError:
    try:
        # Then try the nested import
        from function_cloud.function_cloud.web.app import create_app
    except ImportError:
        # If both fail, define a placeholder function that will raise a more helpful error
        def create_app(*args, **kwargs):
            raise ImportError(
                "Could not import create_app. This might be due to a deployment issue. "
                "Please check that the function_cloud package is installed correctly."
            )

def get_app():
    """
    Get the Flask application for the Function Cloud web interface.
    """
    return create_app()

__all__ = ["create_app", "get_app"]
