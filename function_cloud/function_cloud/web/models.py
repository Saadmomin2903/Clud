"""
Models for Function Cloud (FC) web interface.
"""

from typing import Optional

# Optional imports for web interface
try:
    from flask_login import UserMixin
    HAS_FLASK_LOGIN = True
except ImportError:
    HAS_FLASK_LOGIN = False
    # Create a mock UserMixin class
    class UserMixin:
        @property
        def is_authenticated(self):
            return True
        
        @property
        def is_active(self):
            return True
        
        @property
        def is_anonymous(self):
            return False
        
        def get_id(self):
            return str(self.id)


class User(UserMixin):
    """User model for Function Cloud."""
    
    def __init__(self, id: str, email: str, name: str, token: Optional[str] = None):
        """
        Initialize a user.
        
        Args:
            id (str): The user's ID.
            email (str): The user's email.
            name (str): The user's name.
            token (str, optional): The user's token.
        """
        self.id = id
        self.email = email
        self.name = name
        self.token = token
