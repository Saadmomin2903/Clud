"""
Web interface for Function Cloud (FC).
"""

from .app import create_app

def get_app():
    """
    Get the Flask application for the Function Cloud web interface.
    """
    return create_app()

__all__ = ["create_app", "get_app"]
